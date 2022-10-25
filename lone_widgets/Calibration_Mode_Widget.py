from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
from aux_scripts.DAQ import DAQ
import nidaqmx
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType
import numpy as np
import os

import time


class calibration_mode(QWidget):
    """
    This is my widget.
    """
    
    def __init__(self):
        super().__init__()
        
        self.global_layout = QHBoxLayout(self)
        
        self.daq=DAQ()
        
        SizePolicy=QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        
        #addons container
        containeradd=QGroupBox("Extra Controls")
        self.layout1=QVBoxLayout(containeradd)
        containeradd.setSizePolicy(SizePolicy)
        self.global_layout.addWidget(containeradd)
        
        
        #file name
        self.filelabel=QLabel(self)
        self.filelabel.setText('File Name')
        self.layout1.addWidget(self.filelabel)
        
        self.filename=QLineEdit(self)
        self.filename.setText('')
        self.layout1.addWidget(self.filename)
        
        #sample rate
        self.samplelabel=QLabel(self)
        self.samplelabel.setText('Sample Rate (kHz)')
        self.layout1.addWidget(self.samplelabel)
        
        self.samplerate=QLineEdit(self)
        self.samplerate.setText('')
        self.layout1.addWidget(self.samplerate)
        
        #self.samplerate.returnPressed.connect(self.update_sample_rate)
        
        #acquisition time
        self.acqlabel=QLabel(self)
        self.acqlabel.setText('Acquisition Time (s)')
        self.layout1.addWidget(self.acqlabel)
        
        self.acqtime=QLineEdit(self)
        self.acqtime.setText('')
        self.layout1.addWidget(self.acqtime)
        
        #button
        
        self.recording_button=QToolButton(self)
        self.recording_button.setText('Start Recording')
        self.layout1.addWidget(self.recording_button)
        self.recording_button.clicked.connect(self.start_reco)
        
        
        ##########################################################################################
        
        #graph container
        containergraph=QGroupBox("Data Recording")
        self.layout2=QVBoxLayout(containergraph)
        self.global_layout.addWidget(containergraph)
        
        # graph itself
        self.layout3=QVBoxLayout(self)
        
        self.graphWidget = pg.PlotWidget()
        
        self.layout3.addWidget(self.graphWidget)

        
        self.graphWidget.setBackground('w')
        
        self.graphWidget.showGrid(x = True, y = True, alpha = 1.0)

        pen = pg.mkPen(color=(255, 0, 0))
        pen1= pg.mkPen(color=(0, 255, 0))
        pen2= pg.mkPen(color=(0, 0, 255))
        self.data_line =  self.graphWidget.plot(np.array([]), pen=pen)
        self.data_line1 =  self.graphWidget.plot(np.array([]), pen=pen1)
        self.data_line2 =  self.graphWidget.plot(np.array([]), pen=pen2)
        
        self.layout2.addLayout(self.layout3)
        
        #buttons
        self.layout_buttons=QHBoxLayout(self)
        
        self.acq_button=QToolButton(self)
        self.acq_button.setText('Start Tracking')
        
        self.reset_button=QToolButton(self)
        self.reset_button.setText('Reset')
        
        self.acq_button.clicked.connect(self.button_pressed)
        self.layout_buttons.addWidget(self.acq_button)
        self.reset_button.clicked.connect(self.reset_d)
        self.layout_buttons.addWidget(self.reset_button)
        
        
        self.layout2.addLayout(self.layout_buttons)
        
    def thread_func(self):
        self.thread=QThread()
        self.worker=Worker_cal()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start_tracking)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.data.connect(self.update_plot_data)
        self.thread.start()
    
    def update_plot_data(self,data_retrieved):
        self.data_line.setData(data_retrieved[0])
        self.data_line1.setData(data_retrieved[1])
        self.data_line2.setData(data_retrieved[2])# Update the data
        
    def reset_d(self):
        self.data_line.setData(np.array([]))
        self.data_line1.setData(np.array([]))
        self.data_line2.setData(np.array([]))
    
    def button_pressed(self):
        if self.acq_button.text()=='Stop Tracking':
            self.acq_button.setText('Start Tracking')
            self.daq.task.close()
            self.worker.stop()
            self.thread.exit()
        else:
            self.daq=DAQ()
            self.thread_func()
            self.acq_button.setText('Stop Tracking')
            print(self.acq_button.text())
    
    def start_reco(self):
        self.worker.rec_start(int(self.acqtime.text()),int(self.samplerate.text()),self.filename.text())
    
    def closeEvent(self, event):
        self.worker.stop()
        self.thread.exit()
        event.accept()
        
class Worker_cal(QWidget):
    finished=pyqtSignal()
    data=pyqtSignal(np.ndarray)
    
    def __init__(self,acq=4,sr=10,file='a'):
        super(Worker_cal,self).__init__()
        self.daq=DAQ()
        self.acq=acq
        self.sr=sr*1000
        self.file=file
        self.rec_flag=False
        self.data_rec=np.empty([3, 1])
        self.n_points=self.sr*self.acq
        self.i=0
        
    
    def callback(self,task_handle, every_n_samples_event_type,number_of_samples, callback_data):
        data_out = np.empty(shape=(3, number_of_samples))
        self.reader.read_many_sample(data_out,number_of_samples)
        self.data.emit(data_out)
        
        if self.rec_flag==True:
            self.i+=number_of_samples
            np.savetxt(self.filei, np.column_stack(data_out),delimiter='\t')
            self.filei.write("\n")
            #self.data_rec=np.concatenate((self.data_rec,data_out),axis=1)
            #print(len(self.data_rec[0]))
            if self.i==self.n_points:
                self.rec_flag=False
                
                #self.file_save(self.data_rec[0,1:],self.file,self.sr)
                print('Done')
            #print(self.data_rec)
            
        return 0
    
    def start_tracking(self):
        self.daq.task.timing.cfg_samp_clk_timing(rate=self.sr,
                                                 sample_mode=AcquisitionType.CONTINUOUS,
                                                samps_per_chan=self.n_points)
        
        
        self.reader = AnalogMultiChannelReader(self.daq.task.in_stream)
        self.daq.task.register_every_n_samples_acquired_into_buffer_event(1000,self.callback)
        self.daq.task.start()
        
        
    def file_save(self,filename,sr):
        default_dir =""
        default_filename = os.path.join(default_dir, filename)
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file", default_filename, "(*.dat)")
        self.filei = open(filepath,'a')
        self.filei.write('Samples per channel: ' + str(sr) +'\nX\tY\tSUM\n')
        
    
    def start(self):
        self.flag=True
        
    def stop(self):
        self.finished.emit()
        self.daq.task.stop()
        self.daq.task.close()
        self.flag=False
        
    def rec_start(self,acq,sr,file):
        self.acq=acq
        self.sr=sr*1000
        self.file=file
        self.file_save(self.file,self.sr)
        self.rec_flag=True
                  
qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
    
if __name__ == "__main__": 
    #start the widget
    ui = calibration_mode()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()