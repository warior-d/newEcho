from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QSlider, QAction, qApp, QToolBar
import newReady as myWidget

# file main.py
class MainWindow(QMainWindow):


    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.settings = myWidget.Settings()
        self.myWidget = myWidget.Main()

        self.exitAction = QAction(QIcon('exit.png'), 'Exit', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)
        self.OpenAction = QAction(QIcon('exit.png'), 'Open', self)

        self.mainmenu = self.menuBar()
        # File ->
        self.menuFile = self.mainmenu.addMenu('File')
        # File -> Open
        self.menuOpen = self.menuFile.addMenu('Open...')
        # File -> Open -> Open Map File
        self.openMapFileAction = QAction(QIcon('open.png'), 'Map File', self)
        self.openMapFileAction.triggered.connect(self.createGrid)
        self.menuOpenMap = self.menuOpen.addAction(self.openMapFileAction)
        # File -> Open -> Open Depth File
        self.menuOpenDepth = self.menuOpen.addAction('Depth File')
        # File.actions
        self.menuFile.addAction(self.exitAction)

        # Settings ->
        self.menuSettings = self.mainmenu.addMenu('Settings')
        self.menuGridAction = QAction(QIcon('grid.png'), 'Add Grid', self)
        self.menuGridAction.triggered.connect(self.createGrid)
        self.menuGrid = self.menuSettings.addAction(self.menuGridAction)

        #self.toolbar = self.addToolBar('Exit')

        self.setCentralWidget(self.myWidget)

        self.statusBar = self.statusBar()
        self.statusBar.showMessage(str(self.settings.getGridScale()))

        self.scale = QSlider(self)
        self.scale.invertedControls()
        self.scale.setMinimum(1)
        self.scale.setMaximum(9)
        self.scale.setPageStep(1)
        self.scale.setSliderPosition(self.settings.getScale())
        self.scale.setTickInterval(1)
        self.scale.setOrientation(QtCore.Qt.Vertical)
        self.scale.setTickPosition(QtWidgets.QSlider.TicksAbove)

        self.scale.setGeometry(1580, 320, 22, 300)
        self.scale.valueChanged.connect(self.updateScale)


    def updateScale(self):
        current_scale = self.scale.value()
        self.myWidget.updateScale(current_scale)
        self.statusBar.showMessage(str(self.settings.getGridScale()) + 'm')

    def createGrid(self):
        self.myWidget.createGrid()



if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())