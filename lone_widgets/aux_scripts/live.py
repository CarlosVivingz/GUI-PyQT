import cv2
import numpy as np
from PyQt5.QtGui import QImage
from PyQt5.QtCore import pyqtSignal,QThread
from pylablib.devices import uc480 #uc480 dll's needed

uc480.list_cameras()
cam = uc480.UC480Camera()

class LiveFeed(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture()
        while self._run_flag:
            frame=cam.snap()
            self.change_pixmap_signal.emit(frame)
            #cv2.waitKey(1)
        cap.release()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()