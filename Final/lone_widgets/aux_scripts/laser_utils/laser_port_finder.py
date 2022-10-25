import serial.tools.list_ports

def port_finder():
    ports = serial.tools.list_ports.comports()
    output='' 
    for port, desc, hwid in sorted(ports):
        if 'serial' in desc.lower():
            output=port
    return output