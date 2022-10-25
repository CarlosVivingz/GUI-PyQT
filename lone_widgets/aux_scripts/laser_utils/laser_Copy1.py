import serial
import time
import os
from .laser_port_finder import port_finder

class mwLaser():
    
    def __init__(self):
        super().__init__()
        output=port_finder()
        
        self.port = serial.Serial(output,timeout=0.15) # Open serial port which is connected to the device
        self.port.baudrate = 57600
        self.current = 0
        self.power = 0
        self.TEC_temperature = 0
        self.TEC_current = 0
        self.status='Ready'
        self.laser_status()
    
    def laser_status(self):
        b=b"\x0f\x10\x11\x05\x80\x10\x02\x00\x00\xb8\xf0"
        self.port.write(b)
        #time.sleep(0.15) # do not remove
        statuse=''
        read=self.port.read_until()
        if len(read)==0:
            pass
        else:
            a=read
           
        dig= a[-3] if len(str(a[-2]))>len(str(a[-3])) else a[-2]
        if dig in [36,66,28]:
            statuse='Disabled'
        if dig in [7,71]:
            statuse='Hibernating'
        if dig in [5,53,37,117,45]:
            statuse='Active'
        if dig in [2]:
            statuse='Ready'
        if dig in [67,69,29]:
            statuse='Configuring'
        else:
            pass
        
        self.status=statuse
        
    def update_current(self):
        b=b"\x0F\x11\xFF\x03\x80\xA1\x00\x34\xF0"
        self.port.write(b)
        #time.sleep(0.15)
        read=self.port.read_until()
        if len(read)==0:
            pass
        else:
            self.current=read[-3]
        
    def update_power(self):
        b=b"\x0F\x11\xFF\x03\x80\xA2\x00\x35\xF0"
        self.port.write(b)
        #time.sleep(0.15)
        read=self.port.read_until()
        if len(read)==0:
            pass
        else:
            self.power=read[-3]
    
    def update_TEC_temperature(self):
        b=b"\x0F\x11\xFF\x03\x80\xA4\x00\x37\xF0"
        self.port.write(b)
        #time.sleep(0.15)
        read=self.port.read_until()
        if len(read)==0:
            pass
        else:
            self.TEC_temperature=read[-3]/10
    
    def update_TEC_current(self):
        b=b"\x0F\x11\xFF\x03\x80\xA5\x00\x38\xF0"
        self.port.write(b)
        #time.sleep(0.15)
        #self.port.read_until()
        read=self.port.read_until()
        if len(read)==0:
            pass
        else:
            self.TEC_current=7600*(read[-3]*(2.5/2**10)-1.25)/100
    
    def set_TEC_temperature(self,x):
        h1=hex(x)[2:]
        h2=hex(246-(200-x))[2:]
        stringo="0F101105B0750200" + h1 + h2 + 'F0'
        b=bytes.fromhex(stringo)
        self.port.write(b)
        self.port.read_until()
        #time.sleep(0.15)
        
    def return_data(self):
        self.update_current()
        self.update_power()
        self.update_TEC_temperature()
        self.update_TEC_current()
        self.laser_status()
        return [self.current,self.power,self.TEC_temperature,self.TEC_current,self.status]
        
    def set_current(self,x):
        if x<=197:
            h1=hex(x)[2:]
            h2=hex(145-(100-x))[2:]
            stringo="0F11FF07A0720400" + h1 + "0000" + h2 + 'F0'
            b=bytes.fromhex(stringo)
            self.port.write(b)
            self.port.read_until()
            #time.sleep(0.15)
        else:
            h1=hex(x)[2:]
            h2=hex(69-(251-x))[2:]
            stringo="0F101105B0720200" + h1 + h2 + 'F0'
            b=bytes.fromhex(stringo)
            self.port.write(b)
            self.port.read_until()
            #time.sleep(0.15)
        
    def enable(self):
        b=b"\x0F\x11\xFF\x03\x40\x15\x00\x68\xF0"
        self.port.write(b)
        self.port.read_until()
        
    def disable(self):
        b=b"\x0F\x11\xFF\x03\x40\x16\x00\x69\xF0"
        self.port.write(b)
        self.port.read_until()
    
    def reset(self):
        if self.port.isOpen() == False:
            self.port = serial.Serial(output,timeout=0.15) # Open serial port which is connected to the device
            self.port.baudrate = 57600
        #time.sleep(0.15)
        b=b"\x0F\x11\xFF\x03\x40\x14\x00\x67\xF0"
        self.port.write(b)
        self.port.read_until()
        
    def hibernate(self):
        self.disable()
        #time.sleep(0.100)
        b=b"\x0F\x11\xFF\x03\x40\x13\x00\x66\xF0"
        self.port.write(b)
        self.port.read_until()
        #if self.port.isOpen() == True:
            #self.port.close()
    
    def close_port(self):
        self.port.close()
        print("\nSerial port closed")