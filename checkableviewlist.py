import sys
from PyQt6.QtWidgets import (QApplication, QListView)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

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
                check_status_list.append(1 if item.checkState() == Qt.CheckState.Checked else 0)
                text_list.append(item.text())
        print(check_status_list, text_list)
        return check_status_list, text_list
    
    def updateItemStatus(self):
        self.status_list, self.text_list = self.getItemStatus()
    
if __name__ == "__main__":
    from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
    class MainWidget(QWidget):
        def __init__(self):
            super().__init__()

            layout = QVBoxLayout()

            self.checkableListView = CheckableListView()
            layout.addWidget(self.checkableListView)

            self.addButton = QPushButton("Add Item")
            self.addButton.clicked.connect(self.addItem)
            layout.addWidget(self.addButton)

            self.setLayout(layout)

        def addItem(self):
            self.checkableListView.addItem("haha")

    app = QApplication(sys.argv)
    mainWidget = MainWidget()
    mainWidget.show()
    sys.exit(app.exec())