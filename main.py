#  This program implements the ability to switch keyboard layouts with only one key press.
#
#  Copyright (C) 2024-2026 Oleksii Sylichenko (a.silichenko@gmail.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "Oleksii Sylichenko"
__copyright__ = "Copyright © 2024-2026 Oleksii Sylichenko"
__license__ = "GNU GPL v3+"
__version__ = "1.1"

import logging
from logging import FileHandler, Logger
from typing import List

import keyboard_layout_controller
import paths
from config_reader import Config
from constants import IS_DEV_MODE
from keyboard_layout_monitor import KeyboardLayoutMonitor
from keyboard_listener import KeyboardListener

from onekey_layout_switcher.models import LayoutInfo
from onekey_layout_switcher.utils import FlagUtil, KlidResolver, LayoutInfoUtil
from tray_icon import TrayIcon


def logging_config() -> None:
    date_format: str = '%Y-%m-%d %H:%M:%S'
    log_format: str = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    logging.basicConfig(format=log_format, datefmt=date_format, level=logging.INFO)

    err_log_handler: FileHandler = FileHandler(paths.get_err_log_file_path())
    err_log_handler.setLevel(logging.ERROR)
    err_log_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))

    root_logger: Logger = logging.getLogger()
    root_logger.addHandler(err_log_handler)


def main() -> None:
    logging_config()
    logger: Logger = logging.getLogger(__name__)
    logger.info('Start')
    logger.info(f'{IS_DEV_MODE = }')

    config: Config = Config()

    keyboard_listeners: List[KeyboardListener] = [
        KeyboardListener('ctrl', timeout=config.key_press_timeout)
    ]
    if config.right_ctrl_hkl is not None:
        keyboard_listeners.append(KeyboardListener('right ctrl',
                                                   hkl=config.right_ctrl_hkl,
                                                   timeout=config.key_press_timeout))
    if config.right_shift_hkl is not None:
        keyboard_listeners.append(KeyboardListener('right shift',
                                                   hkl=config.right_shift_hkl,
                                                   timeout=config.key_press_timeout))

    def start_listen() -> None:
        for listener in keyboard_listeners:
            listener.start_listen()

    def stop_listen() -> None:
        for listener in keyboard_listeners:
            listener.stop_listen()

    klid_resolver: KlidResolver = KlidResolver()
    layout_info_util: LayoutInfoUtil = LayoutInfoUtil(klid_resolver=klid_resolver)
    flag_util: FlagUtil = FlagUtil()

    active_hkl: int = keyboard_layout_controller.get_active_hkl()
    layout: LayoutInfo = layout_info_util.from_hkl(active_hkl)
    country_code: str = layout.country_code or ''
    if not country_code:
        logger.error(f'Failed to obtain country code: {str(layout)}')

    tray_icon: TrayIcon = TrayIcon(
        flag_util=flag_util,
        start_listen_keyboard=start_listen,
        stop_listen_keyboard=stop_listen,
        country_code=country_code
    )

    monitor: KeyboardLayoutMonitor = KeyboardLayoutMonitor(
        tray_icon=tray_icon,
        layout_info_util=layout_info_util,
        check_interval=config.layout_check_interval
    )
    monitor.start()

    logging.info('Exit')


if __name__ == '__main__':
    main()
