from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Camera_Widget import camera_widget
from Laser_Widget import laser_widget
from Data_Acquisition_Widget import acquisition_widget
from Piezos_Widget import piezo_widget

import sys

class live_mode(QWidget):
    """
    This is my widget.
    """
    def __init__(self):
        super().__init__()
        
        self.global_layout = QGridLayout(self)
        
        #laser container
        containerl=QGroupBox("Laser Controls")
        layout=QHBoxLayout(containerl)
        
        self.laser=laser_widget(self)
        layout.addWidget(self.laser)
        containerl.setLayout(layout)
        
        self.global_layout.addWidget(containerl,0,0)
        
        
        #Data Acquisition
        containeracq=QGroupBox("Data Parameters")
        layout1=QHBoxLayout(containeracq)
        
        self.data=acquisition_widget(self)
        layout1.addWidget(self.data)
        containeracq.setLayout(layout1)
        
        self.global_layout.addWidget(containeracq,1,1)
        
        #camera
        containercam=QGroupBox("Camera")
        layout=QHBoxLayout(containercam)
        
        self.camera=camera_widget()
        layout.addWidget(self.camera)
        containercam.setLayout(layout)
        
        self.global_layout.addWidget(containercam,0,1)
        
        #piezo controls
        containerpiezo=QGroupBox("Piezo Controls")
        layout=QHBoxLayout(containerpiezo)
        
        self.piezo=piezo_widget(self)
        layout.addWidget(self.piezo)
        containerpiezo.setLayout(layout)
        
        self.global_layout.addWidget(containerpiezo,1,0)
        
    def closeEvent(self, event):
        self.laser.closeEvent(event)
        self.camera.closeEvent(event)
        self.piezo.closeEvent(event)
        event.accept()
        
qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
    
if __name__ == "__main__": 
    #start the widget
    ui = live_mode()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()