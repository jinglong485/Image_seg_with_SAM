from PyQt6 import QtGui
from PyQt6.QtWidgets import (QLabel, QListView, QWidget, QVBoxLayout, 
                            QPushButton, QHBoxLayout, QCheckBox,
                            QButtonGroup, QFileDialog, QMessageBox,
                            QLineEdit)
from PyQt6.QtGui import (QPixmap, QPainter, QPen,QStandardItemModel,
                        QStandardItem)
from PyQt6.QtCore import Qt, QRect, QPoint, QStandardPaths
from arrimage import ArrImage
from segment_anything import sam_model_registry, SamPredictor
import numpy as np


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
        self.setFixedSize(512,512)

    def mousePressEvent(self, event):
        self.parent().accept_button.setEnabled(True)
        self.parent().reject_button.setEnabled(True)
        self.parent().mask_name_edit.setEnabled(True)
        self.parent().mask_name_edit.setText("Object")
        if self.draw_points:
            x, y = event.pos().x() , event.pos().y()
            if event.button() == Qt.MouseButton.LeftButton:
                self.include_points.append(QPoint(x,y))
                self.update()
                print(f"{x},{y}")
            elif event.button() == Qt.MouseButton.RightButton:
                self.exclude_points.append(QPoint(x,y))
                self.update()
            self.sendSAMROI()
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
                    self.sendSAMROI()

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
            self.parent().parent().statusBar().showMessage(f"x:{self.mouse_position.x()}, y:{self.mouse_position.y()}")

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

    def getSAMROI(self):
        include_points_xy = [[point.x(), point.y()] for point in self.include_points]
        exclude_points_xy = [[point.x(), point.y()] for point in self.exclude_points]
        points_arr = np.concatenate((np.array(include_points_xy).reshape(-1,2), np.array(exclude_points_xy).reshape(-1,2)))
        label_arr = np.concatenate((np.ones(len(include_points_xy)), np.zeros(len(exclude_points_xy))))
        if not self.rectangle is None:
            include_box_list = [self.rectangle.topLeft().x(), self.rectangle.topLeft().y(), self.rectangle.bottomRight().x(), self.rectangle.bottomRight().y()]
            include_box_arr = np.array(include_box_list).reshape(1,-1)
        else:
            include_box_arr = None
        return points_arr, label_arr, include_box_arr
    
    def sendSAMROI(self):
        self.parent().updateSAMROI(self.getSAMROI())
        self.parent().getSAMMasks()
        self.parent().setUpPixLabes()

class CheckableListView(QListView):

    def __init__(self):
        super().__init__()
        self.model = QStandardItemModel()
        self.setModel(self.model)
        self.model.itemChanged.connect(self.listItemChanged)
        self.status_list = []
        self.text_list = []

    def addItem(self, text):
        item = QStandardItem(text)
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Checked)
        self.model.appendRow(item)
        self.listItemChanged()

    def listItemChanged(self):
        self.updateItemStatus()
        #return should be replaced by parent.update method
        #return self.getItemStatus()

    def getItemStatus(self):
        check_status_list = []
        text_list = []
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            if item is not None:
                check_status_list.append(1 if item.checkState() \
                                         == Qt.CheckState.Checked else 0)
                text_list.append(item.text())
        print(check_status_list, text_list)
        return check_status_list, text_list
    
    def updateItemStatus(self):
        self.status_list, self.text_list = self.getItemStatus()

class PixLabel(QLabel):

    def __init__(self, num):
        super().__init__()
        self.num = num
        self.pixmap = None
        self.text = f"Candidate_{self.num}"
        self.setUpText()
        self.setFixedSize(128,128)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.parent().setCandidateIndexByNum(self.num-1)
            self.parent().setUpMaskedImageToCanvas()
            print(self.num -1)


    def setUpText(self):
        self.setText(self.text)

    def showPixmap(self):
        self.setPixmap(self.pixmap)
        if self.pixmap.height() != 0:
            print(f"plabel height is {self.pixmap.height()}")
            self.setFixedSize(self.pixmap.width(), self.pixmap.height())
        else:
            self.setFixedSize(128, 128)
        

    def updatePixmap(self, arr):
        if not arr is None:
            image = QtGui.QImage(arr, arr.shape[1],\
                                arr.shape[0], arr.shape[1] * 3,\
                                QtGui.QImage.Format.Format_RGB888).rgbSwapped()
            self.pixmap = QPixmap(image)
        else:
            self.pixmap = QPixmap(None)


class MainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initializeUI()
        self.initializeSAMPredictor()
        self.initializeArr()

    def initializeUI(self):
        main_Hlayout = QHBoxLayout(self)
        left_Vlayout = QVBoxLayout()
        middle_Vlayout = QVBoxLayout()
        right_Vlayout = QVBoxLayout()

        self.next_image_button = QPushButton("Next")
        self.previous_image_button = QPushButton("Previous")
        self.image_num_label = QLabel()
        self.draw_points = QCheckBox("Points")
        self.draw_box = QCheckBox("Box")
        left_button_layout = QHBoxLayout()
        left_button_layout.addWidget(self.previous_image_button)
        left_button_layout.addWidget(self.image_num_label)
        left_button_layout.addWidget(self.next_image_button)
        left_button_layout.addWidget(self.draw_points)
        left_button_layout.addWidget(self.draw_box)
        self.draw_method_group = QButtonGroup()
        self.draw_method_group.setExclusive(True)
        self.draw_method_group.addButton(self.draw_points)
        self.draw_method_group.addButton(self.draw_box)
        self.image_canvas = Canvas(self)
        self.image_canvas.setEnabled(False)
        #self.image_canvas.setFixedSize(512,512)
        left_Vlayout.addLayout(left_button_layout)
        left_Vlayout.addWidget(self.image_canvas)

        self.accept_button = QPushButton("Accept")
        self.reject_button = QPushButton("Reject")
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.mask_name_edit = QLineEdit()
        self.mask_name_edit.setEnabled(False)
        #self.load_img_to_sam = QPushButton("Load Image to SAM")
        middle_button_layout = QHBoxLayout()
        middle_button_layout.addWidget(self.accept_button)
        middle_button_layout.addWidget(self.reject_button)
        self.candidate_1 = PixLabel(1)
        self.candidate_2 = PixLabel(2)
        self.candidate_3 = PixLabel(3)
        middle_Vlayout.addLayout(middle_button_layout)
        middle_Vlayout.addWidget(self.mask_name_edit)
        #middle_Vlayout.addWidget(self.load_img_to_sam)
        middle_Vlayout.addWidget(self.candidate_1)
        middle_Vlayout.addWidget(self.candidate_2)
        middle_Vlayout.addWidget(self.candidate_3)

        self.item_list = CheckableListView()
        self.export_as_tiff = QPushButton("export tiff")
        self.export_as_npz = QPushButton("export npz")
        right_Vlayout.addWidget(self.item_list)
        right_Vlayout.addWidget(self.export_as_tiff)
        right_Vlayout.addWidget(self.export_as_npz)

        main_Hlayout.addLayout(left_Vlayout)
        main_Hlayout.addLayout(middle_Vlayout)
        main_Hlayout.addLayout(right_Vlayout)

        #default values
        self.draw_points.setChecked(True)

        #signal slot connect
        self.draw_points.stateChanged.connect(self.changeDrawMode)
        self.reject_button.clicked.connect(self.clearCandidates)
        self.accept_button.clicked.connect(self.acceptCandidate)
        self.export_as_tiff.clicked.connect(self.exportDataAsTiff)
        self.export_as_npz.clicked.connect(self.exportDataAsArray)
        #self.load_img_to_sam.clicked.connect(self.loadImageToSAMPredictor)

    def initializeSAMPredictor(self):
        self.model_device = "cpu"
        self.model_type = "vit_b"
        self.sam_check_point_path = None
        self.sam_model = None
        self.predictor = None
        self.points_array = None
        self.points_label_array = None
        self.box_array = None
        self.SAM_model_loaded = False

    def loadSAMModel(self):
        desktop_path = None
        #desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open .pth File",
            desktop_path,
            "PTH Files (*.pth);;All Files (*)",
        )
        #print(file_name)
        self.sam_check_point_path = file_name

    def setSAMModelType(self, model_device, model_type):
        self.model_device = model_device
        self.model_type = model_type
        #print(self.model_device, self.model_type)
    
    def setUpSAMPredictor(self):
        """this takes long time, need disable widget notification and status bar note"""
        if self.sam_check_point_path != "":
            self.sam_model = sam_model_registry[self.model_type](checkpoint=self.sam_check_point_path)
            self.sam_model.to(device=self.model_device)
            self.predictor = SamPredictor(self.sam_model)
            self.SAM_model_loaded = True
            self.parent().statusBar().showMessage("SAM loaded")

    def loadImageToSAMPredictor(self):
        self.parent().statusBar().showMessage("Loading image model")
        self.predictor.set_image(self.arr_image_list[self.arr_image_index].image())
        self.parent().statusBar().showMessage("Image model loaded")

    def setPoints(self, points, labels):
        self.points_array = points
        self.points_label_array = labels

    def setBox(self, box):
        self.box_array = box

    def getSAMMasks(self):
        masks, scores, logits = self.predictor.predict(
            point_coords=self.points_array,
            point_labels=self.points_label_array,
            box = self.box_array,
            multimask_output=True,)
        masks_int8 = []
        for mask in masks:
            masks_int8.append(mask.astype(np.uint8))
        self.arr_masks = masks_int8
        print(len(self.arr_masks))
        print(type(self.arr_masks))
        print(self.arr_masks[0].shape)
        print(self.arr_masks[0].dtype)

    def changeDrawMode(self, state):
        if state:
            self.image_canvas.setDrawPoints()
        else:
            self.image_canvas.setDrawRect()

    def updateSAMROI(self, ROI_tuple):
        temp_points_array, temp_points_label_array, temp_box_array = ROI_tuple
        self.points_array = self.arr_resize_factor * temp_points_array
        self.points_label_array = temp_points_label_array
        if temp_box_array is None:
            self.box_array = None
        else:
            self.box_array = self.arr_resize_factor * temp_box_array
        print(self.points_array)
        print(self.points_label_array)
        print(self.box_array)

    def initializeArr(self):
        self.arr_image_list = []
        self.arr_image_index = None
        self.arr_resize_factor = None
        #arr_candidate are vars for show masked candidates
        self.arr_candidate_128_list = []
        self.arr_candidate_512_list = []
        self.arr_candidate_index = 0
        #arr_makss receives masks generated from predictor
        self.arr_masks = []
        #diretory path for exporting masks
        self.export_path = None

    def addArrImage(self, path):
        arr_img = ArrImage()
        arr_img.loadImage(path)
        self.arr_image_index = len(self.arr_image_list)
        self.arr_image_list.append(arr_img)
        self.arr_resize_factor = arr_img.resizeFactor()
        self.image_canvas.setEnabled(True)

    def setUpArrImageToCanvas(self):
        self.image_canvas.setUpPixmap(self.arr_image_list[self.arr_image_index].maskedResizedImage())
        self.image_canvas.update()

    def setUpMaskedImageToCanvas(self):
        if len(self.arr_candidate_512_list) != 0:
            self.image_canvas.setUpPixmap(self.arr_candidate_512_list[self.arr_candidate_index])
            self.image_canvas.update()

    def loadArrImage(self):
        if self.SAM_model_loaded:
            desktop_path = None
            #desktop_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DesktopLocation)
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open Image File",
                desktop_path,
                "Images (*.png *.jpg *.tiff);;All Files (*)",
            )
            if file_name != "":
                self.addArrImage(file_name)
                self.setUpArrImageToCanvas()
                self.loadImageToSAMPredictor()
                self.item_list.model.clear()
        else:
            QMessageBox.warning(self, "SAM model not loaded",
                    "Load SAM model first!",
                    QMessageBox.StandardButton.Ok)
            
    def setUpPixLabes(self):
        self.arr_candidate_512_list, self.arr_candidate_128_list = self.arr_image_list[self.arr_image_index].maskedCandidatesImage(self.arr_masks)
        #self.image_canvas.setUpPixmap(self.arr_candidate_512_list[self.arr_candidate_index])
        self.setUpMaskedImageToCanvas()
        self.candidate_1.updatePixmap(self.arr_candidate_128_list[0])
        self.candidate_1.showPixmap()
        self.candidate_2.updatePixmap(self.arr_candidate_128_list[1])
        self.candidate_2.showPixmap()
        self.candidate_3.updatePixmap(self.arr_candidate_128_list[2])
        self.candidate_3.showPixmap()

    def setCandidateIndexByNum(self, num):
        self.arr_candidate_index = num
        print(self.arr_candidate_index)

    def clearCandidates(self):
        self.arr_candidate_128_list = []
        self.arr_candidate_512_list = []
        self.arr_candidate_index = 0
        #arr_makss receives masks generated from predictor
        self.arr_masks = []
        self.candidate_1.updatePixmap(None)
        self.candidate_1.showPixmap()
        self.candidate_1.setUpText()
        self.candidate_2.updatePixmap(None)
        self.candidate_2.showPixmap()
        self.candidate_2.setUpText()
        self.candidate_3.updatePixmap(None)
        self.candidate_3.showPixmap()
        self.candidate_3.setUpText()
        self.image_canvas.clearCanvas()
        self.setUpArrImageToCanvas()
        self.accept_button.setEnabled(False)
        self.reject_button.setEnabled(False)
        self.mask_name_edit.setEnabled(False)
    
    def acceptCandidate(self):
        self.arr_image_list[self.arr_image_index].addMask(self.arr_masks[self.arr_candidate_index], self.mask_name_edit.text())
        self.item_list.addItem(self.arr_image_list[self.arr_image_index].masks_name[-1])
        self.clearCandidates()

    def setExportPath(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if path != "":
            self.export_path = path
        
    def exportDataAsTiff(self):
        if not self.arr_image_index is None:
            if self.export_path is None:
                self.setExportPath()
                if self.export_path != "" and self.export_path is not None:
                    self.arr_image_list[self.arr_image_index].exportMaskAsTiff(self.export_path)
                    self.parent().statusBar().showMessage("File saved as tiff")
            else:
                self.arr_image_list[self.arr_image_index].exportMaskAsTiff(self.export_path)
                self.parent().statusBar().showMessage("File saved as tiff")
        else:
            QMessageBox.warning(self, "Image not loaded",
                    "Load image before saving!",
                    QMessageBox.StandardButton.Ok)

    def exportDataAsArray(self):
        if not self.arr_image_index is None:
            if self.export_path is None:
                self.setExportPath()
                if self.export_path != "" and self.export_path is not None:
                    self.arr_image_list[self.arr_image_index].exportMaskAsArray(self.export_path)
                    self.parent().statusBar().showMessage("File saved as npz")
            else:
                self.arr_image_list[self.arr_image_index].exportMaskAsArray(self.export_path)
                self.parent().statusBar().showMessage("File saved as npz")
        else:
            QMessageBox.warning(self, "Image not loaded",
                    "Load image before saving!",
                    QMessageBox.StandardButton.Ok)
        




if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = MainWidget()
    window.show()
    sys.exit(app.exec())

        
