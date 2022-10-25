from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from nidaqmx.stream_readers import AnalogMultiChannelReader
from nidaqmx.constants import AcquisitionType, WAIT_INFINITELY
import numpy as np
import os
from aux_scripts.DAQ import DAQ

import sys

class acquisition_widget(QWidget):
    """
    This is my widget.
    """
    def __init__(self, parent=None):
        super().__init__()
        
        
        self.global_layout = QHBoxLayout(self)
        
        layout1=QVBoxLayout(self)
        
        #file name
        self.filelabel=QLabel(self)
        self.filelabel.setText('File Name')
        layout1.addWidget(self.filelabel)
        
        self.filename=QLineEdit(self)
        self.filename.setText('')
        layout1.addWidget(self.filename)
        
        #sample rate
        self.samplelabel=QLabel(self)
        self.samplelabel.setText('Sample Rate (kHz)')
        layout1.addWidget(self.samplelabel)
        
        self.samplerate=QLineEdit(self)
        self.samplerate.setText('')
        layout1.addWidget(self.samplerate)
        
        self.samplerate.returnPressed.connect(self.update_sample_rate)
        
        #acquisition time
        self.acqlabel=QLabel(self)
        self.acqlabel.setText('Acquisition Time (s)')
        layout1.addWidget(self.acqlabel)
        
        self.acqtime=QLineEdit(self)
        self.acqtime.setText('')
        layout1.addWidget(self.acqtime)
        
        #button
        
        self.recording_button=QToolButton(self)
        self.recording_button.setText('Start Recording')
        self.recording_button.clicked.connect(self.thread)
        
        layout1.addWidget(self.recording_button)
        
        
        self.global_layout.addLayout(layout1)
        
        #self.setFixedWidth(300)
        #self.setFixedHeight(300)
    def thread(self):
        self.thread=QThread()
        self.worker=Worker_DAQ(int(self.acqtime.text()),int(self.samplerate.text()),self.filename.text())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.start_recording)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        
    def update_sample_rate(self):
        if float(self.samplerate.text())<=10:
            self.samplerate.setText(str(self.samplerate.text()))
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('The sample rate is too high')
            msg.setWindowTitle("Error")
            msg.exec_()
            self.samplerate.setText('0')
    
    def closeEvent(self, event):
        self.worker.stop()
        self.thread.exit()
        event.accept()
        
class Worker_DAQ(QWidget):
    finished=pyqtSignal()
    data=pyqtSignal()
    
    def __init__(self,acq,sr,file):
        super(Worker_DAQ,self).__init__()
        self.daq=DAQ()
        self.acq=acq
        self.sr=sr*1000
        self.file=file
    
    def start_recording(self,parent=None):
        print('baby')
        n_points=self.sr*self.acq
        self.daq.task.timing.cfg_samp_clk_timing(rate=self.sr,
                                sample_mode=AcquisitionType.CONTINUOUS,
                                samps_per_chan=n_points)
        
        self.daq.task.start()
        reader = AnalogMultiChannelReader(self.daq.task.in_stream)
        self.data_out = np.empty(shape=(3, n_points))
        reader.read_many_sample(data = self.data_out,number_of_samples_per_channel=n_points,timeout=WAIT_INFINITELY)
        
        self.daq.task.stop()
        
        print('Acquisition Sucessful')
        
        self.file_save(self.data_out,self.file,self.sr)
        
    def file_save(self,data,filename,sr):
        default_dir =""
        default_filename = os.path.join(default_dir, filename)
        filepath, _ = QFileDialog.getSaveFileName(self, "Save file", default_filename, "(*.dat)")
        
        if filepath:
            np.savetxt(filepath, np.column_stack(data),delimiter='\t',header='Samples per channel: ' + str(sr) +'\nX\tY\tSUM')
        self.finished.emit()
        
qapp = QCoreApplication.instance()
if qapp is None:
    qapp = QApplication(sys.argv)
    
if __name__ == "__main__": 
    #start the widget
    ui = acquisition_widget()
    #show the widget
    ui.show()
    #start the events loop
    qapp.exec_()