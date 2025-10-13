"""Module containing 'CoincidenceCounter' class"""

import serial
import time

class MotorDriver():
    """
    Python driver for the motor controller that is part of the qubitekk quantum 
    mechanics lab kit (quantum optics)
    """
    def __init__(self, port: str, comm_delay: float = 0.0):
        """
        Constructor method for 'MotorDriver' class

        Args:
            port (str): Port the hardware is connected to
        """
        self.serial = serial.Serial(
            port = port,
            baudrate = 9600,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            timeout = 1,
            xonxoff = False,
            rtscts = False,
            dsrdtr =False,
            write_timeout = 1
        )
        self.comm_wait = comm_delay
        time.sleep(0.1)
        self.serial.write(b":LEDO\n")

    def __del__(self):
        """Destructor for 'MotorDriver' class"""
        self.serial.close()

    @property
    def position(self):
        """Getter for position of motor"""
        self.serial.write(b'POSI?\n')
        time.sleep(self.comm_wait)
        position_str = str(self.serial.readline().decode('utf-8')[:-1])
        if position_str is '':
            position_str = self.position
        return float(position_str)

    @position.setter
    def position(self, value):
        """Setter for position of motor"""
        if value < 1 or value > 29:
            raise ValueError(f"Motor position must be between 0 and 29 mm")
        self.serial.write(f':MOVE ABS {value}\n'.encode())
        time.sleep(self.comm_wait)