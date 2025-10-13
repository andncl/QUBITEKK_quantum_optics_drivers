"""Module containing 'CoincidenceCounter' class"""

import serial
import time

class CoincidenceCounter():
    """
    Python driver for the CC1 coincidence counter. Part of the qubitekk quantum 
    mechanics lab kit (quantum optics)
    """
    def __init__(self, port: str, comm_delay: float = 0.0):
        """
        Constructor method for 'CoincidenceCounter' class

        Args:
            port (str): Port the hardware is connected to
        """
        self.serial = serial.Serial(
            port = port,
            baudrate = 19200,
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
        self._dwell_time = None

    def __del__(self):
        """Destructor for 'CoincidenceCounter' class"""
        self.serial.close()

    @property
    def dwell_time(self):
        """Getter for integration time of coincidence counter"""
        self.serial.write(b'DWEL?\n')
        time.sleep(self.comm_wait)
        time_in_ms = str(self.serial.readline().decode('utf-8')[:-3])
        self._dwell_time = float(int(time_in_ms)*1e-3)
        return f"{time_in_ms} ms"

    @dwell_time.setter
    def dwell_time(self, value):
        """Setter for integration time of coincidence counter"""
        if value < 0.1 or value > 30:
            raise ValueError(f"Dwell time must be between 0.1 and 30s")
        self.serial.write(f':DWEL {value}\n'.encode())
        self._dwell_time = value
        time.sleep(self.comm_wait)

    @property
    def coincidence_window(self):
        """Getter for coincidence_window time of coincidence counter"""
        self.serial.write(b'WIND?\n')
        time.sleep(self.comm_wait)
        time_in_ns = str(self.serial.readline().decode('utf-8')[:-1])
        return f"{time_in_ns}"

    @coincidence_window.setter
    def coincidence_window(self, value):
        """Setter for coincidence_window in ns time of coincidence counter"""
        if value not in range(1,9):
            raise ValueError(f"Coincidence window must be between 1 and 8 ns")
        self.serial.write(f':WIND {value}\n'.encode())
        time.sleep(self.comm_wait)

    @property
    def ch1_delay(self):
        """Getter for ch1_delay time in ns of coincidence counter"""
        self.serial.write(b'DELA?\n')
        time.sleep(self.comm_wait)
        time_in_ns = str(self.serial.readline().decode('utf-8')[:-1])
        return f"{time_in_ns}"

    @ch1_delay.setter
    def ch1_delay(self, value):
        """Setter for ch1_delay time in ns of coincidence counter"""
        if value not in [0, 2, 4, 6, 8, 10, 12,14]:
            raise ValueError(f"Ch1_delay window must be even number in [0,14]")
        self.serial.write(f':DELA {value}\n'.encode())
        time.sleep(self.comm_wait)

    def measure_channels(self):
        """
        Measures counts of both channels
        
        Returns:
            int: Counts of channel 1
            int: Counts of channel 2
            int: Coincidences between channels
        """
        self.serial.write(b':COUN:ON\n')
        time.sleep(self.comm_wait + self._dwell_time)
        self.serial.readline().decode('utf-8')[:-1]
    
        self.serial.write(b'COUN:C1?\n')
        time.sleep(self.comm_wait)
        ch1 = self.serial.readline().decode('utf-8')[:-1]
    
        self.serial.write(b'COUN:C2?\n')
        time.sleep(self.comm_wait)
        ch2 = self.serial.readline().decode('utf-8')[:-1]

        self.serial.write(b'COUN:CO?\n')
        time.sleep(self.comm_wait)
        coincidences = self.serial.readline().decode('utf-8')[:-1]
        return int(ch1), int(ch2), int(coincidences)

    def query(self, cmd):
        self.serial.write(f"{cmd}\n".encode())
        time.sleep(self.comm_wait)
        return self.serial.readline().decode('utf-8')[:-1]

    def close(self):
        """Closes serial connection to hardware and deletes object"""
        self.serial.close
        self.__del__()
