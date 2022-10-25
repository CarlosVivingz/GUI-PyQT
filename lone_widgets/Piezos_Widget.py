from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import numpy as np
from aux_scripts.piezos import KPA, KPZ, list_devices

import sys

class piezo_widget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.kpa=KPA(list_devices()[3])
        self.kpz_x=KPZ(list_devices()[0])
        self.kpz_y=KPZ(list_devices()[2])
        self.kpz_z=KPZ(list_devices()[1])
        
        self.kpz_x.connect()
        self.kpz_y.connect()
        self.kpz_z.connect()
        self.kpa.connect()
        
        self.global_layout = QHBoxLayout(self)
        self.layout1=QVBoxLayout(self)
        self.layout2=QVBoxLayout(self)
        
        
        sizePolicy=QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        # displacement controls 
        self.dislabel=QLabel(self)
        self.dislabel.setText('Enter Displacement')
        self.dislabel.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.dislabel)
        
        #x axis
        self.xlabel=QLabel(self)
        self.xlabel.setText('X-axis(V)')
        self.xlabel.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.xlabel)
        
        self.x_axis=QLineEdit(self)
        self.x_axis.setText('')
        self.x_axis.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.x_axis)
        
        #y axis
        self.ylabel=QLabel(self)
        self.ylabel.setText('Y-axis(V)')
        self.ylabel.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.ylabel)
        
        self.y_axis=QLineEdit(self)
        self.y_axis.setText('')
        self.y_axis.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.y_axis)
        
        #z axis
        self.zlabel=QLabel(self)
        self.zlabel.setText('Z-axis(V)')
        self.zlabel.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.zlabel)
        
        self.z_axis=QLineEdit(self)
        self.z_axis.setText('')
        self.z_axis.setSizePolicy(sizePolicy)
        self.layout1.addWidget(self.z_axis)
        
        #buttons
        
        self.turn_button=QToolButton(self)
        self.turn_button.setText('Turn On')
        self.turn_button.setSizePolicy(sizePolicy)
        self.turn_button.clicked.connect(self.turn_on)
        self.layout2.addWidget(self.turn_button)
        
        self.reset_button=QToolButton(self)
        self.reset_button.setText('Reset')
        self.reset_button.setSizePolicy(sizePolicy)
        self.layout2.addWidget(self.reset_button)
        
        self.zero_button=QToolButton(self)
        self.zero_button.setText('Zero')
        self.zero_button.setSizePolicy(sizePolicy)
        self.layout2.addWidget(self.zero_button)
        ################################ Plot ###################################################
        
        self.layout3=QVBoxLayout(self)
        
        self.graphWidget = pg.PlotWidget()
        
        self.layout3.addWidget(self.graphWidget)

        self.x = [ self.kpa.get_position()[0] ] 
        self.y = [ self.kpa.get_position()[1] ]
        
        self.graphWidget.setBackground('w')
        
        self.graphWidget.showGrid(x = True, y = True, alpha = 1.0)
        
        self.graphWidget.setXRange(-0.008, 0.008, padding=0)
        self.graphWidget.setYRange(-0.008, 0.008, padding=0)

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen, symbol='o')
        
        self.global_layout.addLayout(self.layout1)
        self.global_layout.addLayout(self.layout2)
        self.global_layout.addLayout(self.layout3)
        
        #self.setFixedWidth(300)
        #self.setFixedHeight(200)
        self.thread()
    
    def thread(self):
        self.thread=QThread()
        self.worker=Worker_kpa(self.kpa)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.update)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.data.connect(self.update_plot_data)
        self.thread.start()
    
    def update_plot_data(self,data_retrieved):
        self.x = [ data_retrieved[0] ]
        self.y = [ data_retrieved[1] ]
        self.data_line.setData(self.x, self.y)  # Update the data
    
    def turn_on(self):
        print([float(self.x_axis.text()),float(self.y_axis.text()),float(self.z_axis.text())])
        self.kpz_x.set_output_voltages(float(self.x_axis.text()))
        self.kpz_y.set_output_voltages(float(self.y_axis.text()))
        self.kpz_z.set_output_voltages(float(self.z_axis.text()))
        
    def closeEvent(self, event):
        self.kpa.close()
        self.kpz_x.disable()
        self.kpz_y.disable()
        self.kpz_z.disable()
        self.kpz_x.close()
        self.kpz_y.close()
        self.kpz_z.close()
        self.worker.stop()
        self.thread.quit()
        print('Closed, bby!')
        event.accept()
        

class Worker_kpa(QObject):
    finished=pyqtSignal()
    data=pyqtSignal(list)
    
    def __init__(self,kpa):
        super(Worker_kpa,self).__init__()
        self.kpa=kpa
        self.flag=True
        
    def update(self):
        while self.flag:
            #QThread.sleep(1)
            data=self.kpa.get_position()
            self.data.emit([ data[0],data[1] ])
        self.finished.emit()
    
    def start(self):
        self.flag=True
        
    def stop(self):
        self.flag=False
        #self.kpa.close()


qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
    
if __name__ == "__main__": 
    #start the widget
    ui = piezo_widget()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()