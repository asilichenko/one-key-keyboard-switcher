#  This program implements the ability to switch keyboard layouts with only one key press.
#
#  Copyright (C) 2024 Oleksii Sylichenko (a.silichenko@gmail.com)
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
__copyright__ = "Copyright © 2024 Oleksii Sylichenko"
__license__ = "GNU GPU v3+"
__version__ = "1.0"

import logging
from config_reader import Config
from keyboard_listener import KeyboardListener
from keyboard_layout_monitor import KeyboardLayoutMonitor

ERR_LOG_FILENAME = 'error.log'


def logging_config():
    date_format = "%Y-%m-%d %H:%M:%S"
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(format=log_format, datefmt=date_format, level=logging.INFO)  #

    err_log_handler = logging.FileHandler(ERR_LOG_FILENAME)
    err_log_handler.setLevel(logging.ERROR)
    err_log_handler.setFormatter(logging.Formatter(fmt=log_format, datefmt=date_format))

    root_logger = logging.getLogger()
    root_logger.addHandler(err_log_handler)


if __name__ == '__main__':
    logging_config()
    logger = logging.getLogger(__name__)
    logger.info("Start")

    config = Config()
    config.read_ini()

    keyboard_listeners = [
        KeyboardListener('ctrl', timeout=config.key_press_timeout)
    ]
    if config.right_ctrl_lang is not None:
        keyboard_listeners.append(KeyboardListener('right ctrl',
                                                   lang_id=config.right_ctrl_lang,
                                                   timeout=config.key_press_timeout))
    if config.right_shift_lang is not None:
        keyboard_listeners.append(KeyboardListener('right shift',
                                                   lang_id=config.right_shift_lang,
                                                   timeout=config.key_press_timeout))


    def start_listen():
        for listener in keyboard_listeners:
            listener.start_listen()


    def stop_listen():
        for listener in keyboard_listeners:
            listener.stop_listen()


    monitor = KeyboardLayoutMonitor(start_listen, stop_listen, config.layout_check_interval)
    monitor.start()

    logging.info("Exit")
