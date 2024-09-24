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

import logging
from logging import Logger
from typing import Callable, Optional

import keyboard
import keyboard_layout_controller

logger: Logger = logging.getLogger(__name__)

TIMEOUT: float = 0.2
"""If a key was pressed longer than this value in seconds, then do not change the keyboard layout."""


class KeyboardListener:
    _on_press_remove: Optional[Callable] = None
    """Function that removes 'on press' listener."""

    _on_release_remove: Optional[Callable] = None
    """Function that removes 'on release' listener."""

    def __init__(self, key_name: str, lang_id: int = None, timeout: float = None) -> None:
        if lang_id is None:
            logger.info('Set listener for round switch on "%s"', key_name)
        else:
            logger.info('Set listener for "%s" on "%s"', hex(lang_id), key_name)

        self._timeout: float = timeout if timeout is not None else TIMEOUT
        self._key_name: str = key_name
        """Name of the observed key."""
        self._key_down_time: float = 0
        """Time when the key was pressed down."""
        self._lang_id: int = lang_id
        """See LANGID: https://learn.microsoft.com/en-us/windows/win32/msi/localizing-the-error-and-actiontext-tables"""

    def start_listen(self) -> None:
        if self._on_press_remove is None:
            self._on_press_remove = keyboard.on_press(self._on_key_press)

        if self._on_release_remove is None:
            self._on_release_remove = keyboard.on_release_key(self._key_name, self._on_key_release)

    def stop_listen(self) -> None:
        if self._on_press_remove is not None:
            self._on_press_remove()
            self._on_press_remove = None

        if self._on_release_remove is not None:
            self._on_release_remove()
            self._on_release_remove = None

    def _is_timeout(self, key_release_time: float) -> bool:
        """
        Checks if a key has been pressed longer than the specified timeout.

        :param key_release_time: The time when the key was released
        :return: True if the key is pressed or has been pressed longer than the specified timeout, otherwise False.
        """

        duration: float = key_release_time - self._key_down_time
        return duration > self._timeout

    def _on_key_press(self, event) -> None:
        """Activates when any key is being pressed down."""

        if self._key_name == event.name:
            if not self._key_down_time:  # record the time of the key down hit and skip holding
                self._key_down_time = event.time
        else:
            self._key_down_time = 0

    def _on_key_release(self, event) -> None:
        if self._is_timeout(event.time):
            self._key_down_time = 0
            return
        self._key_down_time = 0

        if self._lang_id is not None:
            keyboard_layout_controller.set_layout(self._lang_id)
        else:
            keyboard_layout_controller.set_next_layout()
