import sys
import os

sys.path.append(os.path.join(os.getcwd(),'lone_widgets'))

#interface 2.0
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qdarkstyle
from lone_widgets.Calibration_Mode_Widget import calibration_mode
from lone_widgets.Live_Mode_Widget import live_mode

#import breeze_resources

class interface(QWidget):
    """
    This is my widget.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Ferdinand")
        
        #layout principal
        self.global_layout = QHBoxLayout(self)
        
        #initiate tabs
        splash.showMessage('Seting up Live Mode...')
        self.live=live_mode()
        splash.showMessage('Seting up Calibration Mode...')
        self.calibration=calibration_mode()
        
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        
        
        self.tabs.addTab(self.tab1,"Live Mode")
        self.tabs.addTab(self.tab2,"Calibration Mode")
        self.tabs.addTab(self.tab3,"Classification Mode")
        self.tabs.addTab(self.tab4,"Settings")        
        
        #tab1- Live mode
        
        self.tab1.layout = QHBoxLayout(self)
        self.tab1.layout.addWidget(self.live)
        self.tab1.setLayout(self.tab1.layout)
        self.global_layout.addWidget(self.tabs)
        self.setLayout(self.global_layout)
        
        #tab2- Calibration Mode
        self.tab2.layout = QHBoxLayout(self)
        self.tab2.layout.addWidget(self.calibration)
        self.tab2.setLayout(self.tab2.layout)
        self.global_layout.addWidget(self.tabs)
        self.setLayout(self.global_layout)
    
        
    def closeEvent(self, event):
        close = QMessageBox.question(self,"Quit","Are you sure want to stop process?",QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            self.live.closeEvent(event)
            event.accept()
        else:
            event.ignore()
        
###################################################################
qapp = QCoreApplication.instance()
qapp.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

if qapp is None:
    qapp = QApplication(sys.argv)
    #file = QFile(":/dark/stylesheet.qss")
    #file.open(QFile.ReadOnly | QFile.Text)
    #stream = QTextStream(file)
    
if __name__ == "__main__": 
    
    pixmap= QPixmap('transferir.jpg')
    splash= QSplashScreen(pixmap)
    splash.show()
    splash.showMessage('Loading...')
    
    #start the widget
    ui = interface()
    splash.showMessage('Starting...')
    #show the widget
    ui.show()
    splash.finish(ui)
    #start the event loop
    qapp.exec_()