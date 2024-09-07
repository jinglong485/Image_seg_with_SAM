import sys
import cv2
from PyQt6 import QtGui
from PyQt6.QtWidgets import (QApplication, QLabel, QVBoxLayout, QPushButton, 
                            QWidget)
from PyQt6.QtGui import (QPixmap, QPainter, QPen)
from PyQt6.QtCore import Qt, QRect, QPoint

class Canvas(QLabel):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.pixmap = None #QPixmap
        self.setMouseTracking(True)
        self.mouse_position = QPoint(-1, -1)
        self.include_points = []
        self.exclude_points = []
        self.rectangle = None
        self.draw_points = True
        self.rect_start_point = None
        self.rect_end_point = None

    def mousePressEvent(self, event):
        if self.draw_points:
            x, y = event.pos().x() , event.pos().y()
            if event.button() == Qt.MouseButton.LeftButton:
                self.include_points.append(QPoint(x,y))
                self.update()
                print(f"{x},{y}")
            elif event.button() == Qt.MouseButton.RightButton:
                self.exclude_points.append(QPoint(x,y))
                self.update()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.rect_start_point = event.pos()
    
    def mouseReleaseEvent(self, event):
        if not self.draw_points:
            if event.button() == Qt.MouseButton.LeftButton:
                self.rect_end_point = event.pos()
                if self.rect_start_point and self.rect_end_point:
                    #the rect always starts from topleft, rect_abs gives absolute topleft
                    x_point_list = [self.rect_start_point.x(), self.rect_end_point.x()]
                    y_point_list = [self.rect_start_point.y(), self.rect_end_point.y()]
                    self.rect_abs_start_point = QPoint(min(x_point_list), min(y_point_list))
                    self.rect_abs_end_point = QPoint(max(x_point_list), max(y_point_list))
                    self.rectangle = \
                        QRect(self.rect_abs_start_point, self.rect_abs_end_point)
                    self.update()

    def mouseMoveEvent(self, event):
        x, y = event.pos().x(), event.pos().y()
        self.mouse_position = QPoint(x, y)
        #pass this to parent widget
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        if not self.pixmap == None:
            painter.drawPixmap(0,0, self.width(), self.height(), self.pixmap)
        painter.setPen(QPen(Qt.GlobalColor.green, 5))
        for point in self.include_points:
            painter.drawPoint(point)
        painter.setPen(QPen(Qt.GlobalColor.red, 5))
        for point in self.exclude_points:
            painter.drawPoint(point)
        painter.setPen(QPen(Qt.GlobalColor.blue,2))
        if not self.rectangle == None:
            painter.drawRect(self.rectangle)
        if self.mouse_position.x() != -1 and self.mouse_position.y() != -1:
            painter.setPen(QPen(Qt.GlobalColor.cyan, 1, Qt.PenStyle.DashLine))
            painter.drawLine(self.mouse_position.x(), 0, self.mouse_position.x(), self.height())
            painter.drawLine(0, self.mouse_position.y(), self.width(), self.mouse_position.y())

    def clearCanvas(self):
        self.include_points.clear()
        self.exclude_points.clear()
        self.rectangle = None
        self.update()

    def setUpPixmap(self, arr):
        image = QtGui.QImage(arr, arr.shape[1],\
                            arr.shape[0], arr.shape[1] * 3,\
                            QtGui.QImage.Format.Format_RGB888).rgbSwapped()
        self.pixmap = QPixmap(image)
        self.setFixedSize(self.pixmap.width(), self.pixmap.height())

    def setDrawPoints(self):
        self.draw_points = True

    def setDrawRect(self):
        self.draw_points = False













if __name__ == "__main__":

    class MainWindow(QWidget):

        def __init__(self):
            img_path = "./images/img3.png"
            arr_image = cv2.imread(img_path)
            super().__init__()
            layout = QVBoxLayout()
            self.canvas = Canvas()
            self.clear = QPushButton("clear")
            self.mode = QPushButton("mode")
            layout.addWidget(self.canvas)
            layout.addWidget(self.clear)
            layout.addWidget(self.mode)
            self.clear.clicked.connect(self.canvas.clearCanvas)
            self.mode.clicked.connect(self.changemode)
            self.canvas.setUpPixmap(arr_image)
            self.setLayout(layout)

        def changemode(self):
            self.canvas.draw_points = not self.canvas.draw_points

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())