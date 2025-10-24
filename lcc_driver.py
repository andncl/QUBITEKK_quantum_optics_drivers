import numpy as np
from ctypes import *
import serial
from LCC25_COMMAND_LIB import *

# Load DLL
LCC25Lib = cdll.LoadLibrary("LCC25CommandLib_x64.dll")

# --- Define all DLL function signatures ---

cmdList = LCC25Lib.List
cmdList.restype = c_int
cmdList.argtypes = [c_char_p, c_int]

cmdOpen = LCC25Lib.Open
cmdOpen.restype = c_int
cmdOpen.argtypes = [c_char_p, c_int, c_int]

cmdClose = LCC25Lib.Close
cmdClose.restype = c_int
cmdClose.argtypes = [c_int]

cmdIsOpen = LCC25Lib.IsOpen
cmdIsOpen.restype = c_int
cmdIsOpen.argtypes = [c_char_p]

cmdGetVoltage1 = LCC25Lib.GetVoltage1
cmdGetVoltage1.restype = c_int
cmdGetVoltage1.argtypes = [c_int, POINTER(c_double)]

cmdGetVoltage2 = LCC25Lib.GetVoltage2
cmdGetVoltage2.restype = c_int
cmdGetVoltage2.argtypes = [c_int, POINTER(c_double)]

cmdSetVoltage1 = LCC25Lib.SetVoltage1
cmdSetVoltage1.restype = c_int
cmdSetVoltage1.argtypes = [c_int, c_double]

cmdSetVoltage2 = LCC25Lib.SetVoltage2
cmdSetVoltage2.restype = c_int
cmdSetVoltage2.argtypes = [c_int, c_double]

cmdGetOutputMode = LCC25Lib.GetOutputMode
cmdGetOutputMode.restype = c_int
cmdGetOutputMode.argtypes = [c_int, POINTER(c_int)]

cmdSetOutputMode = LCC25Lib.SetOutputMode
cmdSetOutputMode.restype = c_int
cmdSetOutputMode.argtypes = [c_int, c_int]

cmdGetModulationFrequency = LCC25Lib.GetModulationFrequency
cmdGetModulationFrequency.restype = c_int
cmdGetModulationFrequency.argtypes = [c_int, POINTER(c_double)]

cmdSetModulationFrequency = LCC25Lib.SetModulationFrequency
cmdSetModulationFrequency.restype = c_int
cmdSetModulationFrequency.argtypes = [c_int, c_double]

cmdGetOutputEnable = LCC25Lib.GetOutputEnable
cmdGetOutputEnable.restype = c_int
cmdGetOutputEnable.argtypes = [c_int, POINTER(c_int)]

cmdSetOutputEnable = LCC25Lib.SetOutputEnable
cmdSetOutputEnable.restype = c_int
cmdSetOutputEnable.argtypes = [c_int, c_int]


# --- Device Listing Function ---
def list_devices():
    """Return list of (serial, COM) connected devices"""
    buf = create_string_buffer(1024, b'\0')
    result = cmdList(buf, 1024)
    if result < 0:
        raise RuntimeError("Failed to list devices")
    data = buf.value.decode("utf-8", "ignore").split(",")
    devices = [(data[i], data[i + 1]) for i in range(0, len(data) - 1, 2)]
    return devices


# --- Main LCC25 Driver Class ---
class LCC25:
    output_mode_map = {0: "modulation", 1: "voltage1", 2: "voltage2"}
    output_mode_inv = {v: k for k, v in output_mode_map.items()}

    def __init__(self, port: str, baud: int = 115200, timeout: int = 1000):
        """Connect to a Thorlabs LCC25 controller via COM port (e.g. 'COM5')."""
        devices = LCC25ListDevices()

        # Find serial number corresponding to this COM port
        serial_no = None
        for sn, com in devices:
            if port.lower() in com.lower():
                serial_no = sn
                break

        if serial_no is None:
            raise ValueError(f"No LCC25 device found on {port}. Available: {devices}")

        # Open device using DLL API
        self.serial_no = serial_no
        self.handle = LCC25Open(serial_no, baud, timeout)
        if self.handle < 0:
            raise ConnectionError(f"Could not open LCC25 with serial {serial_no} on {port}")

        print(f"LCC25 device {serial_no} connected on {port} (handle={self.handle}).")

    def close(self):
        """Close device."""
        if hasattr(self, "handle") and self.handle:
            LCC25Close(self.handle)
            print(f"LCC25 device {self.serial_no} closed.")
            self.handle = None

    # --- Output Mode ---
    @property
    def output_mode(self) -> str:
        """Get current output mode (modulation, voltage1, voltage2)."""
        mode = c_int()
        ret = cmdGetOutputMode(self.handle, byref(mode))
        if ret < 0:
            raise IOError("Failed to get output mode.")
        return self.output_mode_map.get(mode.value, f"Unknown({mode.value})")

    @output_mode.setter
    def output_mode(self, mode_name: str):
        """Set output mode by name (modulation, voltage1, voltage2)."""
        if mode_name not in self.output_mode_inv:
            raise ValueError(f"Invalid mode '{mode_name}'. Must be one of {list(self.output_mode_inv.keys())}")
        mode_code = self.output_mode_inv[mode_name]
        ret = cmdSetOutputMode(self.handle, mode_code)
        if ret < 0:
            raise IOError("Failed to set output mode.")

    # --- Voltage 1 ---
    @property
    def voltage1(self) -> float:
        """Get current voltage 1 value."""
        v = c_double()
        ret = cmdGetVoltage1(self.handle, byref(v))
        if ret < 0:
            raise IOError("Failed to get voltage1.")
        return v.value

    @voltage1.setter
    def voltage1(self, value: float):
        """Set voltage 1 value (0–25 V)."""
        if not (0 <= value <= 25):
            raise ValueError("Voltage1 must be between 0 and 25 V.")
        ret = cmdSetVoltage1(self.handle, value)
        if ret < 0:
            raise IOError("Failed to set voltage1.")

    # --- Voltage 2 ---
    @property
    def voltage2(self) -> float:
        """Get current voltage 2 value."""
        v = c_double()
        ret = cmdGetVoltage2(self.handle, byref(v))
        if ret < 0:
            raise IOError("Failed to get voltage2.")
        return v.value

    @voltage2.setter
    def voltage2(self, value: float):
        """Set voltage 2 value (0–25 V)."""
        if not (0 <= value <= 25):
            raise ValueError("Voltage2 must be between 0 and 25 V.")
        ret = cmdSetVoltage2(self.handle, value)
        if ret < 0:
            raise IOError("Failed to set voltage2.")

    # --- Modulation Frequency ---
    @property
    def modulation_frequency(self) -> float:
        """Get modulation frequency in Hz."""
        f = c_double()
        ret = cmdGetModulationFrequency(self.handle, byref(f))
        if ret < 0:
            raise IOError("Failed to get modulation frequency.")
        return f.value

    @modulation_frequency.setter
    def modulation_frequency(self, value: float):
        """Set modulation frequency (Hz, 5–150 Hz)."""
        if not (5 <= value <= 150):
            raise ValueError("Frequency must be between 5 Hz and 150 Hz.")
        ret = cmdSetModulationFrequency(self.handle, value)
        if ret < 0:
            raise IOError("Failed to set modulation frequency.")
            
    # --- Output Enable ---
    @property
    def output_enable(self) -> bool:
        """Check if output is enabled (True) or disabled (False)."""
        enable_state = c_int()
        ret = cmdGetOutputEnable(self.handle, byref(enable_state))
        if ret < 0:
            raise IOError("Failed to get output enable state.")
        return bool(enable_state.value)

    @output_enable.setter
    def output_enable(self, enable: bool):
        """Enable or disable output."""
        value = 1 if enable else 0
        ret = cmdSetOutputEnable(self.handle, value)
        if ret < 0:
            raise IOError("Failed to set output enable state.")


# --- Example usage ---
if __name__ == "__main__":
    devices = list_devices()
    print("Devices found:", devices)
    if devices:
        serial = devices[0][0]
        lcc = LCC25(serial)

        lcc.output_mode = "voltage1"
        print("Output mode:", lcc.output_mode)

        lcc.voltage1 = 2.0
        print("Voltage1 set to:", lcc.voltage1)

        # Sweep voltage 0–15 V
        for v in np.linspace(0, 15, 100):
            lcc.voltage1 = v

        lcc.close()
