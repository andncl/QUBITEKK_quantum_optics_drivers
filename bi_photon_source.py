"""Module containing 'BiPhotonSource' class"""

import serial
import time

class BiPhotonSource():
    """
    Python driver for the QUBITEKK bi-photon source models 2.4.
    Part of the qubitekk quantum mechanics lab kit (quantum optics)
    """
    def __init__(self, port: str, comm_delay: float = 1.0):
        """
        Initialize the QES 2.4 interface.

        Args:
            port (str): The COM port (e.g., "COM3" or "/dev/ttyUSB0")
            comm_delay (float): Delay (s) between write and read operations
        """
        self.serial = serial.Serial(
            port=port,
            # baudrate=115200, for new source
            baudrate = 115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            write_timeout=1
        )
        self.comm_wait = comm_delay

        # Internal cached values
        self._temperature = None
        self._temperature_setpoint = None
        self._current = None
        self._voltage = None
        self._fault_status = None
        self._heating_state = None
        self._firmware_version = None

        self._laser_on = False
        self._laser_power = None
        self._laser_current = None
        self._laser_status = None

    # -------------------------------------------------------------------------
    # Helper methods
    # -------------------------------------------------------------------------

    def _write(self, cmd: str):
        """Send a command (no query expected)."""
        self.serial.write((cmd + "\r\n").encode("utf-8"))
        time.sleep(self.comm_wait)

    def _query(self, cmd: str) -> str:
        """Send a query and return decoded response."""
        self.serial.write((cmd + "\r\n").encode("utf-8"))
        time.sleep(self.comm_wait)
        return self.serial.readline().decode("utf-8").strip()

    # -------------------------------------------------------------------------
    # Temperature Control
    # -------------------------------------------------------------------------

    @property
    def temperature(self) -> float:
        """Return the current crystal temperature in °C."""
        response = self._query("TEMP?")
        self._temperature = float(response)
        return self._temperature

    @property
    def temperature_setpoint(self) -> int:
        """Get the crystal temperature setpoint (integer between 10000–50000)."""
        response = self._query("SETP?")
        self._temperature_setpoint = int(response)
        return self._temperature_setpoint

    @temperature_setpoint.setter
    def temperature_setpoint(self, value: int):
        """Set the crystal temperature setpoint."""
        if not 10000 <= value <= 50000:
            raise ValueError("Temperature setpoint must be between 10000 and 50000.")
        self._write(f":SETT {value}")
        self._temperature_setpoint = value

    @property
    def current(self) -> float:
        """Return current reading from I/O board (A)."""
        response = self._query("CURR?")
        self._current = float(response)
        return self._current

    @property
    def voltage(self) -> float:
        """Return voltage reading from I/O board (V)."""
        response = self._query("VOLT?")
        self._voltage = float(response)
        return self._voltage

    @property
    def fault_status(self) -> int:
        """Return 0 (no fault) or 1 (fault in temperature control)."""
        response = self._query("FAUL?")
        self._fault_status = int(response)
        return self._fault_status

    @property
    def heating_state(self) -> str:
        """Return 'H' (heating) or 'C' (cooling)."""
        response = self._query("HORC?")
        self._heating_state = response
        return self._heating_state

    @property
    def firmware_version(self) -> str:
        """Return firmware version of the controller."""
        response = self._query("FIRM?")
        self._firmware_version = response
        return self._firmware_version

    # -------------------------------------------------------------------------
    # Laser Control
    # -------------------------------------------------------------------------

    @property
    def laser_on(self) -> bool:
        """Return True if laser is on, False if off."""
        self._laser_status = self._query("PLST?")
        self._laser_on = "APC" in self._laser_status.upper()
        return self._laser_on

    @laser_on.setter
    def laser_on(self, state: bool):
        """Turn the laser on or off."""
        if state:
            self._write(":PLON")
        else:
            self._write(":PLOF")
        self._laser_on = state

    @property
    def laser_power(self) -> int:
        """Return current laser optical DAC setting (0–8000)."""
        response = self._query("PLDC?")
        self._laser_power = int(response)
        return self._laser_power

    @laser_power.setter
    def laser_power(self, value: int):
        """Set laser optical power (0–8000)."""
        if not 0 <= value <= 8000:
            raise ValueError("Laser power must be between 0 and 8000.")
        self._write(f":PLSD {value}")
        self._laser_power = value

    @property
    def laser_current(self) -> float:
        """Return current laser diode current (mA)."""
        response = self._query("PLCR?")
        self._laser_current = float(response)
        return self._laser_current

    @laser_current.setter
    def laser_current(self, value: int):
        """Set laser diode current (20–120 mA)."""
        if not 20 <= value <= 120:
            raise ValueError("Laser diode current must be between 20 and 120 mA.")
        self._write(f":PLDC {value}")
        self._laser_current = value

    @property
    def laser_status(self) -> str:
        """Return textual laser status (e.g. 'APC', 'OFF')."""
        response = self._query("PLST?")
        self._laser_status = response
        return self._laser_status

    @property
    def laser_id(self) -> str:
        """Return the QES pump laser ID."""
        return self._query("PLID?")

    @property
    def laser_hours(self) -> int:
        """Return operating hours of the laser."""
        return int(self._query("PLOH?"))

    @property
    def laser_turnons(self) -> int:
        """Return the number of times the laser has been turned on."""
        return int(self._query("PLTO?"))

    @property
    def laser_info(self) -> str:
        """Return laser information (firmware, serial number, etc.)."""
        return self._query("PLIN?")

    @property
    def laser_firmware(self) -> str:
        """Return pump laser firmware version."""
        return self._query("PLFM?")

    @property
    def laser_model(self) -> str:
        """Return model number of the QES pump laser."""
        return self._query("PLMD?")

    @property
    def laser_access_level(self) -> int:
        """Return current laser access level."""
        return int(self._query("PLAC?"))

    def enable_autostart(self):
        """Enable QES pump laser autostart after power on."""
        self._write(":PLAO")

    def disable_autostart(self):
        """Disable QES pump laser autostart after power on."""
        self._write(":PLAF")

    def save_settings(self):
        """Save current QES pump laser settings."""
        self._write(":PLSV")

    def change_access_level(self):
        """Change laser access level to 3 (for configuration)."""
        self._write(":PLAC")

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def close(self):
        """Close the serial connection."""
        self.serial.close()
        
        
class BiPhotonSourceOld(): #ToDo This is currently broken. I do suspect the baudrate to be 9600 though.
    """
    Python driver for the QUBITEKK bi-photon source models 2.2.
    Part of the qubitekk quantum mechanics lab kit (quantum optics)
    
    """
    def __init__(self, port: str, comm_delay: float = 1.0):
        """
        Initialize the QES 2.2 interface.

        Args:
            port (str): The COM port (e.g., "COM3" or "/dev/ttyUSB0")
            comm_delay (float): Delay (s) between write and read operations
        """
        self.serial = serial.Serial(
            port=port,
            # baudrate=115200, for new source
            baudrate = 9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
            write_timeout=1
        )
        self.comm_wait = comm_delay

        # Internal cached values
        self._temperature = None
        self._temperature_setpoint = None
        self._current = None
        self._voltage = None
        self._fault_status = None
        self._heating_state = None
        self._firmware_version = None

        self._laser_on = False
        self._laser_power = None
        self._laser_current = None
        self._laser_status = None

    # -------------------------------------------------------------------------
    # Helper methods
    # -------------------------------------------------------------------------

    def _write(self, cmd: str):
        """Send a command (no query expected)."""
        self.serial.write((cmd + "\r\n").encode("utf-8"))
        time.sleep(self.comm_wait)

    def _query(self, cmd: str) -> str:
        """Send a query and return decoded response."""
        self.serial.write((cmd + "\r\n").encode("utf-8"))
        time.sleep(self.comm_wait)
        return self.serial.readline().decode("utf-8").strip()

