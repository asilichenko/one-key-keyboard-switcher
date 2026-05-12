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
import threading
import time

import keyboard_layout_controller
from onekey_layout_switcher.models import LayoutInfo
from onekey_layout_switcher.utils.layout_info_util import LayoutInfoUtil
from tray_icon import TrayIcon

CHECK_INTERVAL: float = 0.5
"""Check keyboard layout every `value` seconds.
Is used when window is changed and language also changed but not by our hotkey"""

logger = logging.getLogger(__name__)


class KeyboardLayoutMonitor:
    """Starts tray icon with flag of the keyboard language.
    Checks keyboard layout and update flag icon if layout is changed."""

    def __init__(
            self,
            tray_icon: TrayIcon,
            layout_info_util: LayoutInfoUtil,
            check_interval: float = None
    ) -> None:
        self._is_active: bool = False
        self._check_interval: float = check_interval if check_interval is not None else CHECK_INTERVAL
        self._tray_icon: TrayIcon = tray_icon
        self._layout_info_util: LayoutInfoUtil = layout_info_util

    def _monitoring(self) -> None:
        prev_active_hkl: int = 0
        while self._is_active:
            active_hkl: int = keyboard_layout_controller.get_active_hkl()
            if active_hkl != prev_active_hkl:
                prev_active_hkl = active_hkl

                layout: LayoutInfo = self._layout_info_util.from_hkl(active_hkl)
                country_code: str = layout.country_code or ''
                if not country_code:
                    logger.error(f'Failed to obtain country code: {str(layout)}')

                self._tray_icon.update_layout(country_code)

            time.sleep(self._check_interval)

    def start(self) -> None:
        """Starts monitoring thread and runs tray icon, which is blocking."""

        self._is_active = True
        threading.Thread(target=self._monitoring, daemon=True).start()

        self._tray_icon.run()  # blocking
        self._is_active = False
