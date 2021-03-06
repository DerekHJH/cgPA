#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QColorDialog,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QRubberBand,
    QWidget,
    QStyleOptionGraphicsItem)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF, QRect, QSize
from PyQt5.Qt import Qt
from PyQt5 import QtCore
import math



class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_cnt = 0
        self.item_dict = {}
        self.selected_id = ''
        self.height = 600

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.p_list_copy = None
        
        self.color = QColor(0, 0, 0)
        
        self.xcenter = 0
        self.ycenter = 0
        self.w = 0
        self.h = 0
        self.xstart = -1
        self.ystart = -1
        
        self.rb = QRubberBand(QRubberBand.Rectangle, self)
        
    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id
    
    def set_pen_color(self, color):
            self.color = color

    def start_draw(self, status, algorithm = ''):
        self.status = status
        self.temp_algorithm = algorithm
        self.temp_id = self.get_id()
        if self.status == 'curve' or self.status == 'polygon':
            self.temp_item = MyItem(self.temp_id, self.status, [], self.temp_algorithm, self.color)
            self.scene().addItem(self.temp_item)

    def finish_draw(self):
        self.temp_id = self.get_id()
    
    def start_modify(self, status, algorithm = ''):
        if self.selected_id == '':
            QMessageBox.information(self, "Info", "Please select an item",
                                    QMessageBox.Ok, QMessageBox.Ok)
            return
        self.status = status
        self.temp_algorithm = algorithm
        self.temp_id = self.selected_id
        self.temp_item = self.item_dict[self.temp_id]

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == QtCore.Qt.LeftButton:
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = self.height - 1 - int(pos.y())
            if self.status == 'line' or self.status == 'ellipse':
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color)
                self.scene().addItem(self.temp_item)
            elif self.status == 'polygon' or self.status == 'curve':
                self.temp_item.p_list.append([x, y])
            elif self.status == 'translate' or self.status == 'rotate' or self.status == 'scale' or self.status == 'clip':
                self.p_list_copy = self.temp_item.p_list
                self.xcenter = x
                self.ycenter = y
                if self.status =='scale' and hasattr(self.p_list_copy, '__len__') and len(self.p_list_copy) > 0:
                    x_min, y_min = self.p_list_copy[0]
                    x_max, y_max = self.p_list_copy[0]
                    for x, y in self.p_list_copy:
                        x_min = min(x_min, x)
                        y_min = min(y_min, y)
                        x_max = max(x_max, x)
                        y_max = max(y_max, y)
                        self.w = x_max - x_min
                        self.h = y_max - y_min
                    self.w += 2
                    self.h += 2
                if self.status == 'clip':
                    self.origin  = event.pos()
                    self.rb.setGeometry(QRect(self.origin, QSize()))
                    self.rb.show()
        elif event.buttons() == QtCore.Qt.RightButton:
            if self.status == 'polygon' or self.status == 'curve':
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
                self.temp_item = MyItem(self.temp_id, self.status, [], self.temp_algorithm, self.color)
                self.scene().addItem(self.temp_item)
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == QtCore.Qt.LeftButton:
            pos = self.mapToScene(event.localPos().toPoint())
            x = int(pos.x())
            y = self.height - 1 - int(pos.y())
            if self.status == 'line' or self.status == 'ellipse':
                self.temp_item.p_list[1] = [x, y]
            elif self.status == 'translate':
                self.temp_item.p_list = alg.translate(self.p_list_copy, x - self.xcenter, y - self.ycenter)
            elif self.status == 'rotate':
                if self.xstart == -1:
                    self.xstart = x
                    self.ystart = y
                else:
                    a = self.xstart - self.xcenter
                    b = self.ystart - self.ycenter
                    c = x - self.xcenter
                    d = y - self.ycenter
                    diff = a * d - b * c
                    Cos = (a * c + b * d) / math.sqrt(a * a + b * b) / math.sqrt(c * c + d * d)
                    angle = math.acos(Cos) / math.pi * 180 
                    if diff < 0:
                        angle = 360 - angle
                    angle = 360 - angle
                    self.temp_item.p_list = alg.rotate(self.p_list_copy, self.xcenter, self.ycenter, angle)
            elif self.status == 'scale':
                s = max(0.1 ,1.0 + (x - self.xcenter) / self.w)
                self.temp_item.p_list = alg.scale(self.p_list_copy, self.xcenter, self.ycenter, s)
            elif self.status == 'clip':
                self.xstart = x
                self.ystart = y
                self.rb.setGeometry(QRect(self.origin, event.pos()).normalized())
                
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line' or self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'rotate':
            self.xstart = -1
            self.ystart = -1
        elif self.status == 'clip':
            self.rb.hide()
            self.temp_item.p_list = alg.clip(self.p_list_copy, self.xcenter, self.ycenter, self.xstart, self.ystart, self.temp_algorithm)
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = QColor(0, 0, 0), parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color
        self.height = 600

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
        
        for i in range(len(item_pixels)):
            item_pixels[i][1] = self.height - 1 - item_pixels[i][1]
        painter.setPen(self.color)
        for p in item_pixels:
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if hasattr(self.p_list, '__len__') and len(self.p_list) > 0:
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            w = 0
            h = 0
            for x, y in self.p_list:
                x_min = min(x_min, x)
                y_min = min(y_min, y)
                x_max = max(x_max, x)
                y_max = max(y_max, y)
                w = x_max - x_min
                h = y_max - y_min
            return QRectF(x_min - 1, self.height - y_max, w + 2, h + 2)
        else:
            return QRectF(0, 0, 1, 1)
    
        


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()

        # 使用QListWidget来记录已有的图元，并用于选择图元。
        #注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.canvas_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # 设置菜单栏
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        save_canvas_act.triggered.connect(self.save_canvas_action)
        exit_act.triggered.connect(self.exit_action)
        
        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        
        ellipse_act.triggered.connect(self.ellipse_action)
        
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    
    def set_pen_action(self):
        self.statusBar().showMessage('设置画笔')
        color = QColorDialog.getColor()
        self.canvas_widget.set_pen_color(color)
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def reset_canvas_action(self):
        self.statusBar().showMessage('重置画布')

        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.canvas_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')
        
    def save_canvas_action(self):
        self.statusBar().showMessage('保存画布')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        file_dialog = QFileDialog()
        filename = file_dialog.getSaveFileName(filter = "Image Files(*.jpg *.png *.bmp)")
        if filename[0]:
            ret = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            ret.save(filename[0])
    
    def exit_action(self):
        self.statusBar().showMessage('退出')
        reply = QMessageBox.question(self, "CG Demo", "是否保存画布",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_canvas_action()
        qApp.quit()

    def line_naive_action(self):
        self.statusBar().showMessage('Naive算法绘制线段')
        self.canvas_widget.start_draw('line', 'Naive')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
    
    def line_dda_action(self):
        self.statusBar().showMessage('DDA算法绘制线段')
        self.canvas_widget.start_draw('line', 'DDA')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def line_bresenham_action(self):
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.canvas_widget.start_draw('line', 'Bresenham')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def ellipse_action(self):
        self.statusBar().showMessage('中点圆算法绘制椭圆')
        self.canvas_widget.start_draw('ellipse')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.canvas_widget.start_draw('polygon', 'DDA')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def polygon_bresenham_action(self):
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.canvas_widget.start_draw('polygon', 'Bresenham')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def curve_bezier_action(self):
        self.statusBar().showMessage('Bezier算法绘制曲线')
        self.canvas_widget.start_draw('curve', 'Bezier')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def curve_b_spline_action(self):
        self.statusBar().showMessage('B-spline算法绘制曲线')
        self.canvas_widget.start_draw('curve', 'B-spline')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        
    def translate_action(self):
        self.statusBar().showMessage('平移')
        self.canvas_widget.start_modify('translate')
    
    def rotate_action(self):
        self.statusBar().showMessage('旋转')
        self.canvas_widget.start_modify('rotate')
    
    def scale_action(self):
        self.statusBar().showMessage('缩放')
        self.canvas_widget.start_modify('scale')
        
    def clip_cohen_sutherland_action(self):
        self.statusBar().showMessage('Cohen_Sutherland算法裁剪')
        self.canvas_widget.start_modify('clip', 'Cohen-Sutherland')
    
    def clip_liang_barsky_action(self):
        self.statusBar().showMessage('Liang_Barsky算法裁剪')
        self.canvas_widget.start_modify('clip', 'Liang-Barsky')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
    
