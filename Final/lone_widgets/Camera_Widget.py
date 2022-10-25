from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pylablib.devices import uc480 #uc480 dll's needed
import cv2
import sys
import numpy as np
from aux_scripts.live import LiveFeed

class camera_widget(QWidget):
    
    def __init__(self):
        super().__init__()
    
        self.setWindowTitle("Camera")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)
        # create a text label
        self.textLabel = QLabel('Camera')

        # create a vertical box layout and add the two labels
        vbox = QVBoxLayout()
        vbox.addWidget(self.image_label)
        vbox.addWidget(self.textLabel)
        # set the vbox layout as the widgets layout
        self.setLayout(vbox)

        # create the video capture thread
        self.thread = LiveFeed()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()
        

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    #@pyqtSlot(np.ndarray)
    def update_image(self, frame):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(frame)
        painter = QPainter(qt_img)
        pen = QPen()
        #pen.setWidth(40)
        pen.setColor(QColor('red'))
        painter.setPen(pen)
        painter.drawLine(270, 0, 270, 600)
        painter.drawLine(0, 247, 600, 247)
        painter.end()
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, frame):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
    
if __name__ == "__main__": 
    #start the widget
    ui = camera_widget()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()