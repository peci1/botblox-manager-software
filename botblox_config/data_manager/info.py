import logging
from argparse import Action, Namespace
from typing import (Any, List)

from .switch_config import SwitchConfigCLI
from ..switch import SwitchChip


class FwRevInfoCLI(SwitchConfigCLI):
    """
    The "read" action that returns MCU firmware revision
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)
        self.append_stop = False
        self.read_back = 1

        self._subparser = self._subparsers.add_parser(
            "fw_rev",
            help="Read firmware revision from the switch MCU",
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[103, 0, 0, 0]]

    def process_response(self, data: Any) -> None:
        logging.info(f'Firmware revision is {data[0]}')
        print(f'{data[0]}')  # noqa: T001


class BoardInfoCLI(SwitchConfigCLI):
    """
    The "read" action that returns the type of switch (nano or switchblox)
    """
    def __init__(self, subparsers: Action, switch: SwitchChip) -> None:
        super().__init__(subparsers, switch)
        self.append_stop = False
        self.read_back = 1

        self._subparser = self._subparsers.add_parser(
            "board_type",
            help="Read board_type from the switch MCU",
        )
        self._subparser.set_defaults(execute=self.apply)

    def apply(self, args: Namespace) -> SwitchConfigCLI:
        return self

    def create_configuration(self) -> List[List[int]]:
        return [[104, 0, 0, 0]]

    def process_response(self, data: Any) -> None:
        switch = "SwitchBlox Nano" if data[0] == ord('n') else "SwitchBlox"
        logging.info(f'The switch type is {switch}')
        print(switch)  # noqa: T001
