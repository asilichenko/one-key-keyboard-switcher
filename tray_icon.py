#  Copyright (C) 2024, 2026 Oleksii Sylichenko (a.silichenko@gmail.com)
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

import logging
import os
import threading
from logging import Logger
from pathlib import Path
from typing import Callable

from PIL import ImageEnhance
from PIL.Image import Image

import constants
import message_box
import paths
from onekey_layout_switcher.utils import FlagUtil

"""https://pystray.readthedocs.io/en/latest/usage.html"""
from pystray import Icon, Menu, MenuItem

logger: Logger = logging.getLogger(__name__)


class TrayIcon:
    ICON_NAME: str = "Keyboard layout country flag"

    PAUSE_TEXT: str = "Pause"
    CONTINUE_TEXT: str = "Continue"
    OPEN_ERR_LOG_FILE: str = "Open error.log"
    EXIT_TEXT: str = "Exit"

    DIM_LEVEL: float = 0.5

    _country_code: str
    _paused: bool = False
    _pause_item_text = PAUSE_TEXT

    def __init__(
            self,
            flag_util: FlagUtil,
            start_listen_keyboard: Callable,
            stop_listen_keyboard: Callable,
            country_code: str
    ) -> None:
        self._flag_util: FlagUtil = flag_util
        self._lock: threading.Lock = threading.Lock()

        self._start_listen_keyboard: Callable = start_listen_keyboard
        self._stop_listen_keyboard: Callable = stop_listen_keyboard

        self._country_code = country_code
        self._icon = Icon(name=self.ICON_NAME,
                          icon=self._make_image(),
                          title=f"{constants.APP_NAME} ({constants.APP_VERSION})",
                          menu=Menu(
                              MenuItem(lambda text: self._pause_item_text, self._toggle_pause),
                              Menu.SEPARATOR,
                              MenuItem(self.OPEN_ERR_LOG_FILE, self._export_err_log),
                              Menu.SEPARATOR,
                              MenuItem(self.EXIT_TEXT, self.stop)
                          ))

    def _make_image(self) -> Image:
        flag: Image = self._flag_util.flag_for(self._country_code)
        return self._apply_dim(flag) if self._paused else flag

    def _apply_dim(self, icon: Image) -> Image:
        icon = ImageEnhance.Brightness(icon).enhance(self.DIM_LEVEL)
        return ImageEnhance.Color(icon).enhance(self.DIM_LEVEL)

    def _toggle_pause(self) -> None:
        with self._lock:
            self._paused = not self._paused
            paused = self._paused
            self._icon.icon = self._make_image()

        if paused:
            self._stop_listen_keyboard()
        else:
            self._start_listen_keyboard()

        self._pause_item_text: str = self.CONTINUE_TEXT if paused else self.PAUSE_TEXT
        self._icon.update_menu()

    @staticmethod
    def _export_err_log() -> None:
        err_log_path: Path = paths.get_err_log_file_path()
        if err_log_path.exists():
            # open file with associated program (usually Notepad)
            os.startfile(str(err_log_path.resolve()))
        else:
            message_box.show_error_message(f"Error log file does not exist:\n{err_log_path}")

    def update_layout(self, country_code: str) -> None:
        with self._lock:
            self._country_code = country_code
            self._icon.icon = self._make_image()

    def run(self) -> None:
        self._start_listen_keyboard()
        self._icon.run()

    def stop(self) -> None:
        self._stop_listen_keyboard()
        self._icon.stop()
