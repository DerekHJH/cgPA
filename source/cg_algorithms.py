#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def symmetry(p_list, axis):
	result = []
	if(axis == 'x'):
		for x, y in p_list:
			result.append([x, -y])
	else:
		for x, y in p_list:
			result.append([-x, y])
	return result

def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
	#handle four specific situations
    if x0 == x1:
        for y in range(min(y0, y1), max(y0, y1) + 1):
            result.append([x0, y])
        return result
		
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0

    if y0 == y1:
        for x in range(x0, x1 + 1):
            result.append([x, y0])
        return result

    dx = x1 - x0
    dy = y1 - y0

    if dx == dy:
        for d in range(dx + 1):
            result.append([x0 + d, y0 + d])
        return result

    if dx == -dy:
        for d in range(dx + 1):
        	result.append([x0 + d, y0 - d])
        return result

	#other ordinary cases
    if algorithm == 'Naive':
        k = (y1 - y0) / (x1 - x0)
        for x in range(x0, x1 + 1):
            result.append([x, int(y0 + k * (x - x0))])

    elif algorithm == 'DDA':
        m = float(dy) / float(dx)
        M = float(dx) / float(dy)
        if dy > 0:
            if dx > dy :
                x = x0
                y = float(y0)
                for i in range(dx + 1):
                    result.append([x, round(y)])
                    x = x + 1
                    y = y + m
            elif dx < dy:
                x = float(x0)
                y = y0
                for i in range(dy + 1):
                    result.append([round(x), y])
                    x = x + M
                    y = y + 1
		
        elif dy < 0:
            neg_dy = -dy
            if dx > neg_dy :
                x = x0
                y = float(y0)
                for i in range(dx + 1):
                    result.append([x, round(y)])
                    x = x + 1
                    y = y + m
            elif dx < neg_dy:
                x = float(x0)
                y = y0
                for i in range(neg_dy + 1):
                    result.append([round(x), y])
                    x = x - M
                    y = y - 1

    elif algorithm == 'Bresenham':
        _2dx = 2 * dx
        _2dy = 2 * dy
        x = x0
        y = y0
        if dy > 0:
            if dx > dy:
                p = _2dy - dx
                inc = _2dy - _2dx
                for i in range(dx + 1):
                    result.append([x, y])
                    if(p > 0):
                        x = x + 1
                        y = y + 1
                        p = p + inc
                    else:
                        x = x + 1
                        y = y
                        p = p + _2dy
            elif dx < dy:
                p = _2dx - dy
                inc = _2dx - _2dy
                for i in range(dy + 1):
                    result.append([x, y])
                    if(p > 0):
                        x = x + 1
                        y = y + 1
                        p = p + inc
                    else:
                        x = x
                        y = y + 1
                        p = p + _2dx
        if dy < 0:
            neg_dy = -dy
            neg_2dy = -_2dy
            if dx > neg_dy:
                p = neg_2dy - dx
                inc = neg_2dy - _2dx
                for i in range(dx + 1):
                    result.append([x, y])
                    if(p > 0):
                        x = x + 1
                        y = y - 1
                        p = p + inc
                    else:
                        x = x + 1
                        y = y
                        p = p + neg_2dy
            elif dx < neg_dy:
                p = _2dx - neg_dy
                inc = _2dx - neg_2dy
                for i in range(neg_dy + 1):
                    result.append([x, y])
                    if(p > 0):
                        x = x + 1
                        y = y - 1
                        p = p + inc
                    else:
                        x = x
                        y = y - 1
                        p = p + _2dx
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    xc = (x0 + x1) // 2
    yc = (y0 + y1) // 2
    rx = abs(x1 - x0) // 2
    ry = abs(y1 - y0) // 2

    rx2 = rx * rx
    ry2 = ry * ry
    p = ry2 * 4 - rx2 * ry * 4 + rx2
    x = 0
    y = ry
    
    while ry2 * x < rx2 * y:
        result.append([x, y])
        if p < 0 :
            p = p + 8 * ry2 * x + 12 * ry2
            x = x + 1
            y = y
        else:
            p = p + 8 * ry2 * x - 8 * rx2 * y + 8 * rx2 + 12 * ry2
            x = x + 1
            y = y - 1

    p = ry2 * (2 * x + 1)**2 + rx2 * (y - 1)**2 * 4 - rx2 * ry2 * 4
    while y >= 0:
        result.append([x, y])
        if p < 0:
            p = p + 8 * ry2 * x - 8 * rx2 * y + 8 * ry2 + 12 * rx2
            x = x + 1
            y = y - 1
        else:
            p = p - 8 * rx2 * y + 12 * rx2
            x = x
            y = y - 1
            
    resultx = symmetry(result, 'x')
    resulty = symmetry(result, 'y')
    result = result + resultx + resulty + symmetry(resultx, 'y')
    result = translate(result, xc, yc)
    return result

def Bezier(p_list, t):
    xt = [[]]
    yt = [[]]
    n = len(p_list) - 1
    for x, y in p_list:
        xt[0].append(x)
        yt[0].append(y)
    for i in range(1, n + 1):
        num = n - i + 1
        xt.append([])
        yt.append([])
        for j in range(0, num):
            xt[i].append(xt[i - 1][j] * (1 - t) + xt[i - 1][j + 1] * t)
            yt[i].append(yt[i - 1][j] * (1 - t) + yt[i - 1][j + 1] * t)
    return [int(xt[n][0]), int(yt[n][0])]

def deBoor_Cox(i, k, u):
    if k == 1:
        return (i <= u and u < i + 1)
    else:
        return (deBoor_Cox(i, k - 1, u) * (u - i) + deBoor_Cox(i + 1, k - 1, u) * (i + k - u)) / (k - 1)

def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    result = []
    x_min, y_min = p_list[0]
    x_max, y_max = p_list[0]
    for x, y in p_list:
        x_min = min(x_min, x)
        x_max = max(x_max, x)
        y_min = min(y_min, y)
        y_max = max(y_max, y)
    h = y_max - y_min + 2
    w = x_max - x_min + 2
    num = (w + h) * int(math.sqrt(len(p_list)))
    if algorithm == "Bezier":
        for t in range(0, num + 1):
            result.append(Bezier(p_list, t / num))
    elif algorithm == 'B-spline':
        k = 3
        n = len(p_list) - 1
        if k > n + 1:
            return []
        for u in range(0, num + 1):
            x, y = 0, 0
            for i in range(n + 1):
                ret = deBoor_Cox(i, k + 1, k + u / num * (n + 1 - k))
                x += p_list[i][0] * ret
                y += p_list[i][1] * ret
                
            result.append([int(x), int(y)])
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    result = []
    for x, y in p_list:
        result.append([x + dx, y + dy])
    return result


def rotate(p_list, xc, yc, angle):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param xc: (int) 旋转中心x坐标
    :param yc: (int) 旋转中心y坐标
    :param angle: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    theta = math.radians(angle)
    result = []
    for x, y in p_list:
        result.append([int(xc + (x - xc) * math.cos(theta) + (y - yc) * math.sin(theta)),
                       int(yc - (x - xc) * math.sin(theta) + (y - yc) * math.cos(theta))])
    return result


def scale(p_list, xc, yc, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param xc: (int) 缩放中心x坐标
    :param yc: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    result = []
    for x, y in p_list:
        result.append([int(x * s + xc * (1 - s)), int(y * s + yc * (1 - s))])
    return result


def clip(p_list, x0, y0, x1, y1, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    if hasattr(p_list, '__len__') == False or len(p_list) == 0:
        return []
    x_min = min(x0, x1)
    x_max = max(x0, x1)
    y_min = min(y0, y1)
    y_max = max(y0, y1)
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    '''        
        0
     3     1
        2
    '''
    if algorithm == 'Cohen-Sutherland':
        area_code0 = ((y0 > y_max) | ((x0 > x_max) << 1) | ((y0 < y_min) << 2) | ((x0 < x_min) << 3))
        area_code1 = ((y1 > y_max) | ((x1 > x_max) << 1) | ((y1 < y_min) << 2) | ((x1 < x_min) << 3))
        if (area_code0 | area_code1) == 0:
            result = [[x0, y0], [x1, y1]]
            return result
        
        if (area_code0 & area_code1) != 0:
            return result
        
        if x0 == x1:
            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            result = [[x0, max(y0, y_min)], [x1, min(y1, y_min)]]
            return result
    
        if y0 == y1:
            result = [[max(x0, x_min), y0], [min(x1, x_max), y1]]
            return result
    
        dx = x1 - x0
        dy = y1 - y0
        m = dy / dx
        mT = dx / dy
        
        area_diff = area_code0 ^ area_code1
        
        
        for i in range(4):
            if area_diff & (1 << i) and i == 0:
                if y0 > y1:
                    x0 = int(x0 + mT * (y_max - y0))
                    y0 = y_max
                else:
                    x1 = int(x1 + mT * (y_max - y1))
                    y1 = y_max
            elif area_diff & (1 << i) and i == 1:
                y1 = int(y1 + m * (x_max - x1))
                x1 = x_max
            elif area_diff & (1 << i) and i == 2:
                if y0 > y1:
                    x1 = int(x1 + mT * (y_min - y1))
                    y1 = y_min
                else:
                    x0 = int(x0 + mT * (y_min - y0))
                    y0 = y_min
            elif area_diff & (1 << i) and i == 3:
                y0 = int(y0 + m * (x_min - x0))
                x0 = x_min
            area_code0 = ((y0 > y_max) | ((x0 > x_max) << 1) | ((y0 < y_min) << 2) | ((x0 < x_min) << 3))
            area_code1 = ((y1 > y_max) | ((x1 > x_max) << 1) | ((y1 < y_min) << 2) | ((x1 < x_min) << 3))
            if (area_code0 | area_code1) == 0:
                result = [[x0, y0], [x1, y1]]
                return result
        
            if (area_code0 & area_code1) != 0:
                return result
        print(x0, y0, x1, y1)
        print(x_min, y_min, x_max, y_max)
    elif algorithm == "Liang-Barsky":
        dx = x1 - x0
        dy = y1 - y0
        u0 = 0
        u1 = 1
        p = [-dx, dx, -dy, dy]
        q = [x0 - x_min, x_max - x0, y0 - y_min, y_max - y0]
        if dx == 0:
            for i in [2, 3]:
                if p[i] < 0:
                    u0 = max(u0, q[i] / p[i])
                else:
                    u1 = min(u1, q[i] / p[i])
        elif dy == 0:
            for i in [0, 1]:
                if p[i] < 0:
                    u0 = max(u0, q[i] / p[i])
                else:
                    u1 = min(u1, q[i] / p[i])
        else:
            for i in range(4):
                if p[i] < 0:
                    u0 = max(u0, q[i] / p[i])
                else:
                    u1 = min(u1, q[i] / p[i])
            
        if(u0 > u1):
            return result
        else:
            result = [[int(x0 + dx * u0), int(y0 + dy * u0)], 
                      [int(x0 + dx * u1), int(y0 + dy * u1)]]
            return result