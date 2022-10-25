import nidaqmx
import numpy as np
import matplotlib.pyplot as plt
import time

class DAQ():
    
    def __init__(self):
        super().__init__()
        
        self.task = nidaqmx.Task()
        #device = "Dev1"
        self.device = 'OTKB' #requires initialization in NI MAX
        self.task.ai_channels.add_ai_voltage_chan(self.device + "/ai0")
        self.task.ai_channels.add_ai_voltage_chan(self.device + "/ai1")
        self.task.ai_channels.add_ai_voltage_chan(self.device + "/ai2")
    
    def start(self):
        self.task.start()
        
    def stop(self):
        self.task.stop()

