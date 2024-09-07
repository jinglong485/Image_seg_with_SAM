from PyQt6.QtWidgets import (QApplication, QMainWindow)
from mywidgets import MainWidget
from PyQt6.QtGui import QAction, QActionGroup, QIcon
import pathlib

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initializeUI()
        self.initializeVar()

    def initializeUI(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        model_menu = menu_bar.addMenu("Model")

        open_file_action = QAction("Open File", self)
        open_folder_action = QAction("Open Directory", self)
        save_folder_action = QAction("Save Directory", self)
        file_menu.addAction(open_file_action)
        file_menu.addAction(open_folder_action)
        file_menu.addAction(save_folder_action)
        load_model_action = QAction("Load Model", self)
        vitb_cuda_action = QAction("vit_b cuda", self)
        vitl_cuda_action = QAction("vit_l cuda", self)
        vith_cuda_action = QAction("vit_h cuda", self)
        vitb_cpu_action = QAction("vit_b cpu", self)
        vitl_cpu_action = QAction("vit_l cpu", self)
        vith_cpu_action = QAction("vit_h cpu", self)
        vitb_mps_action = QAction("vit_b mps", self)
        vitl_mps_action = QAction("vit_l mps", self)
        vith_mps_action = QAction("vit_h mps", self)
        vitb_cpu_action.setCheckable(True)
        vitl_cpu_action.setCheckable(True)
        vith_cpu_action.setCheckable(True)
        vitb_cuda_action.setCheckable(True)
        vitl_cuda_action.setCheckable(True)
        vith_cuda_action.setCheckable(True)
        vitb_mps_action.setCheckable(True)
        vitl_mps_action.setCheckable(True)
        vith_mps_action.setCheckable(True)
        vitb_cpu_action.setChecked(True)
        model_group = QActionGroup(self)
        model_menu.addAction(load_model_action)
        model_group.setExclusive(True)
        model_menu.addSeparator()
        model_menu.addAction(vitb_cuda_action)
        model_menu.addAction(vitl_cuda_action)
        model_menu.addAction(vith_cuda_action)
        model_menu.addAction(vitb_cpu_action)
        model_menu.addAction(vitl_cpu_action)
        model_menu.addAction(vith_cpu_action)
        model_menu.addAction(vitb_mps_action)
        model_menu.addAction(vitl_mps_action)
        model_menu.addAction(vith_mps_action)
        model_group.addAction(vitb_cuda_action)
        model_group.addAction(vitl_cuda_action)
        model_group.addAction(vith_cuda_action)
        model_group.addAction(vitb_cpu_action)
        model_group.addAction(vitl_cpu_action)
        model_group.addAction(vith_cpu_action)
        model_group.addAction(vitb_mps_action)
        model_group.addAction(vitl_mps_action)
        model_group.addAction(vith_mps_action)
        vitb_cpu_action.triggered.connect(self.modelSelect)
        vitl_cpu_action.triggered.connect(self.modelSelect)
        vith_cpu_action.triggered.connect(self.modelSelect)
        vitb_cuda_action.triggered.connect(self.modelSelect)
        vitl_cuda_action.triggered.connect(self.modelSelect)
        vith_cuda_action.triggered.connect(self.modelSelect)
        vitb_mps_action.triggered.connect(self.modelSelect)
        vitl_mps_action.triggered.connect(self.modelSelect)
        vith_mps_action.triggered.connect(self.modelSelect)
        load_model_action.triggered.connect(self.setUpModel)
        self.statusBar().showMessage("Ready")
        self.central_widget = MainWidget()
        self.setCentralWidget(self.central_widget)
        open_file_action.triggered.connect(self.central_widget.loadArrImage)
        save_folder_action.triggered.connect(self.central_widget.setExportPath)
        
        self.setWindowTitle("Image Segement Tool")
        current_directory = str(pathlib.Path(__file__).parent.absolute())
        path = current_directory + '/icon.png'
        self.setWindowIcon(QIcon(path))

    def initializeVar(self):
        self.device_type = "cpu"
        self.model_type = "vit_b"

    def modelSelect(self):
        sender_action = self.sender()
        self.model_type, self.device_type = sender_action.text().split(" ")

    def setUpModel(self):
        self.central_widget.loadSAMModel()
        self.central_widget.setSAMModelType(self.device_type, self.model_type)
        self.central_widget.setUpSAMPredictor()

    

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
