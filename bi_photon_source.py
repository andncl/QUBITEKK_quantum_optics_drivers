"""Module containing 'BiPhotonSource' class"""

import serial
import time

class BiPhotonSource():
    """
    Python driver for the QUBITEKK bi-photon source models 4XXX.
    Part of the qubitekk quantum mechanics lab kit (quantum optics)
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
        self._temperature = None
        self._temperature_setpoint = None

    @property
    def temperature_celcius(self):
        """Getter for crystal temperature"""
        self.serial.write(b'TEMP?\n')
        time.sleep(self.comm_wait)
        temp = str(self.serial.readline().decode('utf-8')[:-1])
        self._temperature = float(int(temp))
        return temp

    @property
    def temperature_setpoint(self):
        """Getter for crystal temperature setpoint. This is NOT a temperature"""
        self.serial.write(b':SETT?\n')
        time.sleep(self.comm_wait)
        setpoint = str(self.serial.readline().decode('utf-8')[:-1])
        self._temperature_setpoint = int(setpoint)
        return setpoint

    @temperature_setpoint.setter
    def temperature_setpoint(self, value):
        """Setter for crystal temperature setpoint. This is NOT a temperature"""
        if value < 0 or value > 30000:
            raise ValueError(f"Temperature setpoint must be between 0 and 30000")
        self.serial.write(f'::SETT {int(value)}\n'.encode())
        self._temperature_setpoint = value
        time.sleep(self.comm_wait)