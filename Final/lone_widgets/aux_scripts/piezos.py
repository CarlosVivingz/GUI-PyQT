import clr 
import sys
import time

#this appends to the global path
sys.path.append("C:\Program Files\Thorlabs\Kinesis")

#This loads the necessary libraries CNET
clr.AddReference("Thorlabs.MotionControl.Benchtop.PiezoCLI")
clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.PiezoCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.PositionAlignerCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.StrainGaugeCLI")
clr.AddReference("System")

from Thorlabs.MotionControl.KCube.PiezoCLI import KCubePiezo
from Thorlabs.MotionControl.KCube.StrainGaugeCLI import KCubeStrainGauge
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.GenericPiezoCLI.Piezo import *
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import KCubePositionAligner


from System import Decimal

def list_devices():
    """Return a list of Kinesis serial numbers"""
    DeviceManagerCLI.BuildDeviceList()
    return DeviceManagerCLI.GetDeviceList()

######################################## KPA ########################################################

clr.AddReference("Thorlabs.MotionControl.KCube.PiezoCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.PositionAlignerCLI")
clr.AddReference("Thorlabs.MotionControl.TCube.StrainGaugeCLI")
clr.AddReference("Thorlabs.MotionControl.GenericPiezoCLI")
clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("System")

from Thorlabs.MotionControl.KCube.PiezoCLI import KCubePiezo
from Thorlabs.MotionControl.TCube.StrainGaugeCLI import TCubeStrainGauge
from Thorlabs.MotionControl.KCube.PiezoCLI import KCubePiezo
from Thorlabs.MotionControl.DeviceManagerCLI import DeviceManagerCLI
from Thorlabs.MotionControl.GenericPiezoCLI.Piezo import *
from Thorlabs.MotionControl.GenericPiezoCLI.StrainGauge import *
from Thorlabs.MotionControl.GenericPiezoCLI.Settings import *
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import KCubePositionAligner
from Thorlabs.MotionControl.KCube.PositionAlignerCLI import * 

class KPA():
    
    def __init__(self, serial_number):
        #initializes from a serial number
        self.serial_number = str(serial_number)
        DeviceManagerCLI.BuildDeviceList()
        
        #initializes the device
        self.device = KCubePositionAligner.CreateKCubePositionAligner(self.serial_number)
        
        #initializes the connected state
        self.connected = False
        
        
    def connect(self):
        #initialize communication
        
        #connect if not connected
        assert not self.connected
        self.device.Connect(self.serial_number)
        self.connected = True
        
        self.device.WaitForSettingsInitialized(5000)
        self.device.StartPolling(250)
        time.sleep(0.5)
        self.device.EnableDevice()
        time.sleep(0.5)
        
        self.device.SetOperatingMode(PositionAlignerStatus.OperatingModes.Monitor, False)
        
        info = self.device.GetDeviceInfo()
        
        print(info)
        
        
        
    def close(self):
        
        if not self.connected:
            print(f"Not closing KPA device {self.serial_number}, it's not open!")
            return
        
        self.device.StopPolling()
        self.device.Disconnect(True)
        
    def get_position(self):
        status = self.device.Status
        time.sleep(0.25)
        read_x,read_y = status.PositionDifference.X, self.device.Status.PositionDifference.Y
        read_sum = status.Sum
        return read_x,read_y,read_sum 

class KPZ():
    
    """
    Builds a K-Cube Piezo device instance for control
    """
    
    def __init__(self, serial_number):
        #serial number
        self.serial_number = str(serial_number)
        
        #builds the list of devices
        DeviceManagerCLI.BuildDeviceList()
        
        #creates a device
        self.device = KCubePiezo.CreateKCubePiezo(self.serial_number)
        
        #connection status
        self.connected = False

    def connect(self):
        #initialize communication
        
        #connect if not connected
        assert not self.connected
        self.device.Connect(self.serial_number)
        self.connected = True
        
        self.device.WaitForSettingsInitialized(5000)
        self.device.StartPolling(250)
        time.sleep(0.5)
        self.device.EnableDevice()
        time.sleep(0.5)
        
        config = self.device.GetPiezoConfiguration(self.serial_number)
        info = self.device.GetDeviceInfo()
        maxVolts = self.device.GetMaxOutputVoltage()
        self.max_v =  Decimal.ToDouble(maxVolts)
        
        return config, info, self.max_v
        
        
    
    def disable(self):
        self.device.DisableDevice()
        
    def close(self):
        
        if not self.connected:
            print(f"Not closing piezo device {self.serial_number}, it's not open!")
            return
        
        self.device.StopPolling()
        self.device.Disconnect(True)

    def set_output_voltages(self, voltage):
        
        if voltage > 0 and voltage<self.max_v:
            #print(self.max_v)
            print(Decimal(voltage))
            i = self.device.SetOutputVoltage(Decimal(voltage))
        else:
            print('Invalid Voltage')
            
    def get_output_voltages(self):
        """Retrieve the output voltages as a list of floating-point numbers"""
        return Decimal.ToDouble(self.device.GetOutputVoltage())