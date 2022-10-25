from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
import queue
from .laser_Copy1 import mwLaser

class Worker(QObject):
    finished= pyqtSignal()
    data=pyqtSignal(list)
    
    def __init__(self,queue,laser):
        super(Worker,self).__init__()
        #self.laser=laser
        self.flag=True
        self.q=queue
        self.laser=laser
    
        
    def update(self):
        while self.flag:
            #time.sleep(0.1)
            item=self.q.get()
            if item=='enable':
                self.laser.enable()
                #self.q.task_done()
            
            if item=='shutdown':
                self.laser.hibernate()
                
            if item=='disable':
                self.laser.disable()
            
            if item=='reset':
                self.laser.reset()
            
            if item=='update':
                data=self.laser.return_data()
                self.data.emit(data)
            
            self.q.task_done()
            #self.q.put('update')
        self.finished.emit()
    
    def start(self):
        self.flag=True
        
    def stop(self):
        self.flag=False