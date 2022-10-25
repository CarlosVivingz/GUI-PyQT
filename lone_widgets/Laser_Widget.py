from PyQt5.QtCore import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
import queue
from aux_scripts.laser_utils.laser_Copy1 import mwLaser
from aux_scripts.laser_utils.send_requests import req_Worker
from aux_scripts.laser_utils.event_handler import Worker

#import breeze_resources

import sys

class laser_widget(QWidget):
    """
    This is my widget.
    """
    def __init__(self, parent=None):
        
        super().__init__()
        
        self.global_layout = QGridLayout(self)
        
        self.laser=mwLaser() ##laser driver
        
        self.q = queue.Queue(maxsize=10) ## Event queue
        
        #######################################################laser box
        container_laser=QGroupBox("Laser")
        vbox_laser= QVBoxLayout(container_laser)
        
        containersimple=QGroupBox()
        hboxsimple=QHBoxLayout(containersimple)
        self.current_display=QLCDNumber(self)
        self.current_display.setGeometry(QRect())
        hboxsimple.addWidget(self.current_display)
        self.labelmAl=QLabel(self)
        self.labelmAl.setText('mA')
        hboxsimple.addWidget(self.labelmAl)
        vbox_laser.addWidget(containersimple)
        
        containersimple1=QGroupBox()
        hboxsimple1=QHBoxLayout(containersimple1)
        self.power_display=QLCDNumber(self)
        self.power_display.setGeometry(QRect())
        hboxsimple1.addWidget(self.power_display)
        self.labelmW=QLabel(self)
        self.labelmW.setText('mW')
        hboxsimple1.addWidget(self.labelmW)
        hboxsimple1.addWidget(containersimple1)
        vbox_laser.addWidget(containersimple1)
        
        ################################################TEC box
        container_TEC=QGroupBox("TEC")
        vbox_TEC= QVBoxLayout(container_TEC)
        containersimple2=QGroupBox()
        
        hboxsimple2=QHBoxLayout(containersimple2)
        self.temp_display=QLCDNumber(self)
        self.temp_display.setGeometry(QRect())
        hboxsimple2.addWidget(self.temp_display)
        self.labelC=QLabel(self)
        self.labelC.setText('ºC')
        hboxsimple2.addWidget(self.labelC)
        vbox_TEC.addWidget(containersimple2)
        
        containersimple3=QGroupBox()
        hboxsimple3=QHBoxLayout(containersimple3)
        self.currTEC_display=QLCDNumber(self)
        self.currTEC_display.setGeometry(QRect())
        hboxsimple3.addWidget(self.currTEC_display)
        self.labelmATEC=QLabel(self)
        self.labelmATEC.setText('mA')
        hboxsimple3.addWidget(self.labelmATEC)
        vbox_TEC.addWidget(containersimple3)
        
        ###############################################current control
        container_input=QGroupBox("Laser Setpoint")
        hbox_set= QHBoxLayout(container_input)
        
        self.labelcur=QLabel(self)
        self.labelcur.setText('Current setpoint:')
        hbox_set.addWidget(self.labelcur)
        
        self.currentv=QLineEdit(self)
        self.currentv.setText('50')
        self.currentv.returnPressed.connect(self.current_changed)
        hbox_set.addWidget(self.currentv)
        
        self.labelmA=QLabel(self)
        self.labelmA.setText('mA')
        hbox_set.addWidget(self.labelmA)
        
        ##################################################temp control
        container_inputt=QGroupBox("TEC Setpoint")
        hbox_set1= QHBoxLayout(container_inputt)
        
        self.labeltemps=QLabel(self)
        self.labeltemps.setText('Temperature setpoint:')
        hbox_set1.addWidget(self.labeltemps)
        
        self.temperaturev=QLineEdit(self)
        self.temperaturev.setText('25')
        self.temperaturev.returnPressed.connect(self.temp_changed)
        hbox_set1.addWidget(self.temperaturev)
        
        self.labelC=QLabel(self)
        self.labelC.setText('ºC')
        hbox_set1.addWidget(self.labelC)
        
        ########################################################buttons
        container_button=QGroupBox()
        hbox_set2= QHBoxLayout(container_button)
        
        self.turn_on_button=QToolButton(self)
        self.turn_on_button.setText('Start Laser')
        self.turn_on_button.clicked.connect(self.laser_clicked)
        #self.turn_on_button.clicked.connect(self.button_state)
        
        container_button2=QGroupBox()
        hbox_set3= QHBoxLayout(container_button2)
        
        self.shutdown_button=QToolButton(self)
        self.shutdown_button.setText('Shutdown')
        self.shutdown_button.clicked.connect(self.shutdown)
        #self.shutdown_button.clicked.connect(self.button_state)
        
        hbox_set2.addWidget(self.turn_on_button)
        hbox_set3.addWidget(self.shutdown_button)

        ######################################################global
        
        self.global_layout.addWidget(container_laser,0,0)
        self.global_layout.addWidget(container_TEC,0,1)
        self.global_layout.addWidget(container_input,1,0)
        self.global_layout.addWidget(container_inputt,1,1)
        self.global_layout.addWidget(container_button,2,1)
        self.global_layout.addWidget(container_button2,2,0)
        
        #self.setFixedWidth(100)
        #self.setFixedHeight(200)
    ###########################################################functions
    #### initial state   
        self.request_thread()
        self.thread()
        #self.button_state()
    #### initiate thread and change status
    
    def thread(self):
        self.thread=QThread()
        self.worker=Worker(self.q,self.laser)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.update)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.data.connect(self.update_status)
        self.thread.start()
    
    def request_thread(self):
        self.reqthread=QThread()
        self.reqworker=req_Worker(self.q)
        self.reqworker.moveToThread(self.reqthread)
        self.reqthread.started.connect(self.reqworker.ask)
        self.reqworker.finished.connect(self.reqthread.quit)
        self.reqworker.finished.connect(self.reqworker.deleteLater)
        self.reqthread.finished.connect(self.reqthread.deleteLater)
        #self.reqworker.data.connect(self.results)
        self.reqthread.start()
    
    
    #### get status from laser class
    def update_status(self,data_retrieved):
        self.laser.current = data_retrieved[0]
        self.laser.power = data_retrieved[1]
        self.laser.TEC_temperature = data_retrieved[2]
        self.laser.TEC_curent=data_retrieved[3]
        self.laser.status=data_retrieved[4]
        self.update_laser_values()
    
    #### 
    def update_laser_values(self):
        self.current_display.display(self.laser.current)
        self.power_display.display(self.laser.power)
        self.currTEC_display.display(self.laser.TEC_current)
        self.temp_display.display(self.laser.TEC_temperature)
        self.status=self.laser.status
        self.button_state()
        
    def button_state(self):
        if self.status=='Disabled' or self.status=='Ready':
            self.turn_on_button.setText('Start Laser')
             
        elif self.status=='Active':
            self.turn_on_button.setText('Disable')

        elif self.status=='Hibernating':
            self.turn_on_button.setText('Restart')
    
        elif self.status=='Configuring':
            self.turn_on_button.setText('Disable')
    
    def shutdown(self):
        self.q.put_nowait('shutdown')
    
    def laser_clicked(self):
        if self.status=='Disabled':
            self.q.put_nowait('enable')
            
        elif self.status=='Active':
            self.q.put_nowait('disable')
            
        elif self.status=='Hibernating':
            self.q.put_nowait('reset')
        
        elif self.status=='Ready':
            self.q.put_nowait('enable')
    
        elif self.status=='Configuring':
            self.q.put_nowait('disable')
    
    #def results(self,data):
        #print(data)
        
    def current_changed(self):
        print(self.currentv.text())
        self.laser.set_current(int(self.currentv.text()))
    
    def temp_changed(self):
        print(self.temperaturev.text())
        self.laser.set_TEC_temperature(int(self.temperaturev.text())*10)
        
    
    ##############################################laser thread
        
    def temp_alarm(self):
        if (float(self.laser.TEC_temperature)<24.9 or (self.laser.TEC_temperature)>25.1):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('TEC Temperature is unstable, shutting down the laser')
            msg.setWindowTitle("Error")
            msg.exec_() 
    
    def closeEvent(self, event):
        self.worker.stop()
        self.thread.quit()
        self.reqworker.stop()
        self.reqthread.quit()
        #self.q.join()
        print('Thread Closed')
        self.laser.close_port()
        event.accept()
    
        
    
qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
#     file = QFile(":/dark/stylesheet.qss")
#     file.open(QFile.ReadOnly | QFile.Text)
#     stream = QTextStream(file)
#     qapp.setStyleSheet(stream.readAll())
    
if __name__ == "__main__": 
    #start the widget
    ui = laser_widget()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()