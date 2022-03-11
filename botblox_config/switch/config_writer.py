import logging
import time
from typing import Any, Generic, List, Tuple, TypeVar

import serial


CommandType = TypeVar('CommandType')


class ConfigWriter(Generic[CommandType]):

    def __init__(self, device_name: str) -> None:
        pass

    def __name__(self) -> str:
        return self.device_description()

    @classmethod
    def device_description(cls: 'ConfigWriter') -> str:
        raise NotImplementedError()

    def write(self, data: CommandType, read_back: int = 0) -> Tuple[bool, Any]:
        raise NotImplementedError()


class TestWriter(ConfigWriter[Any]):
    @classmethod
    def device_description(cls: 'TestWriter') -> str:
        return "Test"

    def write(self, data: CommandType, read_back: int = 0) -> Tuple[bool, Any]:
        return True, [1, 2] if read_back > 0 else None


class UARTWriter(ConfigWriter[List[Any]]):

    def __init__(self, device_name: str) -> None:
        super().__init__(device_name)
        if not device_name.startswith("/dev/"):
            raise ValueError("Wrong UART communication device " + device_name)
        self._device_name = device_name

    @classmethod
    def device_description(cls: 'UARTWriter') -> str:
        return "USB-to-UART converter"

    def write(self, data: List[Any], read_back: int = 0) -> Tuple[bool, Any]:
        """
        Write data commands to serial port.

        Write data to serial port which the UART converter is connected to. The STM32 MCU
        on the SwitchBlox will then be interrupted and carry out the commands

        :param List[List] data: Commands created to write to STM32 MCU
        :return: Flag to indicate whether the write data to serial was successful or not
        """

        with serial.Serial(
            port=self._device_name,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            timeout=30,
            write_timeout=2,
        ) as ser:

            for command in data:
                x = bytes(command)
                ser.write(x)
                time.sleep(0.1)

            condition = ser.read(size=1)

            try:
                condition = list(condition)[0]
            except IndexError:
                logging.error('Failed to read condition message from board')
                return False, None
            else:
                if read_back == 0:
                    if condition == 1:
                        logging.info('Success setting configuration in EEPROM')
                        return True, None
                    elif condition == 2:
                        logging.error('Failed saving configuration in EEPROM')
                        return False, None
                else:
                    if condition == 1:
                        logging.info('Success reading configuration from switch')
                        data = ser.read(size=read_back)
                        return True, list(data)
                    elif condition == 2:
                        logging.error('Failed reading configuration from switch')
                        return False, None
