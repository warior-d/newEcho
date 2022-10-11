from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QButton
from PyQt5.QtGui import QPixmap

class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        screen_width = QApplication.instance().desktop().availableGeometry().width()
        screen_height = QApplication.instance().desktop().availableGeometry().height()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.buttonOpenImageMap = QB(self)
        pixmapMapImage = QPixmap('MapImage.PNG')




    def conn(self):
        print('click')










if __name__ == '__main__':

    import sys
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())