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

import threading
import time
from typing import Optional, Callable

import keyboard_layout_controller
from tray_icon import TrayIcon

CHECK_INTERVAL: float = 0.5
"""Check keyboard layout every `value` seconds.
Is used when window is changed and language also changed but not by our hotkey"""


class KeyboardLayoutMonitor:
    """Starts tray icon with flag of the keyboard language.
    Checks keyboard layout and update flag icon if layout is changed."""

    def __init__(self, start_listen: Callable, stop_listen: Callable, check_interval: float = None) -> None:
        self._monitor_thread: Optional[threading.Thread] = None
        self._check_interval: float = check_interval if check_interval is not None else CHECK_INTERVAL

        self._layout_id: int = keyboard_layout_controller.get_keyboard_layout_id()
        country_id: int = keyboard_layout_controller.extract_country_id(self._layout_id)
        self._tray_icon: TrayIcon = TrayIcon(start_listen, stop_listen, country_id)

    def _monitoring(self) -> None:
        while True:
            layout_id: int = keyboard_layout_controller.get_keyboard_layout_id()
            if layout_id != self._layout_id:
                self._layout_id = layout_id
                country_id: int = keyboard_layout_controller.extract_country_id(self._layout_id)
                self._tray_icon.update_flag(country_id)
            time.sleep(self._check_interval)

    def start(self) -> None:
        """Starts monitoring thread and runs tray icon, which is blocking."""

        if self._monitor_thread is None:
            self._monitor_thread = threading.Thread(target=self._monitoring, daemon=True)
            self._monitor_thread.start()

            self._tray_icon.run()  # blocking
