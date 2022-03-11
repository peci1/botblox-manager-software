import functools
import logging
from argparse import Action, Namespace, SUPPRESS
from typing import (Any, AnyStr, Dict, List)

from .switch_config import SwitchConfigCLI
from ..switch import SwitchChip


def parse_phy(phy_str: AnyStr) -> int:
    num = int(phy_str)  # ValueError can be thrown, but that's expected for non-int inputs
    if (num < 2) or (num > 24):
        raise ValueError("{} is not valid PHY number (2 <= PHY <= 24)")
    return num


def parse_reg(reg_str: AnyStr) -> int:
    num = int(reg_str)  # ValueError can be thrown, but that's expected for non-int inputs
    if (num < 0) or (num > 31):
        raise ValueError("{} is not valid REG number (0 <= REG <= 31)")
    return num


def parse_command(command_str: AnyStr) -> int:
    num = int(command_str)  # ValueError can be thrown, but that's expected for non-int inputs
    if (num < 0) or (num > 19):
        raise ValueError("{} is not valid configuration command number (0 <= command <= 19)")
    return num


class ReadSwitchCLI(SwitchConfigCLI):
    """
    The "read" action that accesses the switch registers.
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)
        self.append_stop = False
        self.read_back = 4
        self._cli_options = {}

        self._subparser = self._subparsers.add_parser(
            "read_switch",
            help="Read switch configuration",
        )

        parse_phy_arg = functools.partial(parse_phy)
        parse_phy_arg.__name__ = "PHY"
        parse_reg_arg = functools.partial(parse_reg)
        parse_reg_arg.__name__ = "REG"

        self._subparser.add_argument(
            'phy',
            type=parse_phy_arg,
            default=SUPPRESS,
            help='''PHY number to read'''
        )
        self._subparser.add_argument(
            'reg',
            type=parse_reg_arg,
            default=SUPPRESS,
            help='''REG number to read'''
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        self._cli_options: Dict = vars(args)
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[102, 1, self._cli_options['phy'], self._cli_options['reg']]]

    def process_response(self, data: Any):
        super().process_response(data)
        print(f'{data}')


class ReadConfigCLI(SwitchConfigCLI):
    """
    The "read" action that accesses the list of configuration commands for the switch.
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)
        self.append_stop = False
        self.read_back = 4
        self._cli_options = {}

        self._subparser = self._subparsers.add_parser(
            "read_config",
            help="Read configuration command",
        )

        parse_command_arg = functools.partial(parse_command)
        parse_command_arg.__name__ = "command"

        self._subparser.add_argument(
            'command',
            type=parse_command_arg,
            default=SUPPRESS,
            help='''Index of stored command to read'''
        )

        self._subparser.add_argument(
            '-t', '--temp',
            action='store_true',
            default=SUPPRESS,
            help='''Access the temporary commands in RAM instead of the permanent storage.'''
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        self._cli_options: Dict = vars(args)
        return self

    def create_configuration(self) -> List[List[int]]:
        num = 3 if 'temp' in self._cli_options and self._cli_options['temp'] else 2
        return [[102, num, self._cli_options['command'], 0]]

    def process_response(self, data: Any):
        type = "RAM" if 'temp' in self._cli_options and self._cli_options['temp'] else "EEPROM"
        logging.info(f'Data read from {type} at position {self._cli_options["command"]} is {data}')
        print(f'{data}')
