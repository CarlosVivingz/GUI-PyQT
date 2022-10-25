from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
import queue

class req_Worker(QObject):
    finished= pyqtSignal()
    data=pyqtSignal(list)
    
    def __init__(self,queue):
        super(req_Worker,self).__init__()
        #self.laser=laser
        self.flag=True
        self.q=queue
        
    def ask(self):
        while self.flag:
            time.sleep(1.2)
            self.q.put('update')
            data=['Sent request']
            self.data.emit(data)
        self.finished.emit()
    
    def start(self):
        self.flag=True
        
    def stop(self):
        self.flag=False