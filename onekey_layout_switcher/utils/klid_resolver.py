#  Copyright (C) 2026 Oleksii Sylichenko (a.silichenko@gmail.com)
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

import ctypes
import threading

from win32api import SendMessage, GetKeyboardLayoutName, GetKeyboardLayout
from win32con import WM_INPUTLANGCHANGEREQUEST
from win32gui import WNDCLASS, GetModuleHandle, RegisterClass, CreateWindow, PumpMessages

kernel32: ctypes.WinDLL = ctypes.windll.kernel32
user32: ctypes.WinDLL = ctypes.windll.user32


class KlidResolver:
    INPUTLANGCHANGE_SYSCHARSET: int = 0x0001
    """Flag means: set the new input locale to be the keyboard layout.
    https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-inputlangchangerequest
    """

    _hwnd: int = 0  # HWND
    _ready: threading.Event = threading.Event()
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def _window_layout_processor_thread(cls) -> None:
        wc = WNDCLASS()
        # noinspection PyPropertyAccess
        wc.lpszClassName = cls.__name__
        # noinspection PyPropertyAccess
        wc.hInstance = GetModuleHandle(None)
        # noinspection PyTypeChecker
        class_atom: int = RegisterClass(wc)
        # noinspection PyTypeChecker
        cls._hwnd = CreateWindow(
            class_atom, wc.lpszClassName,
            0, 0, 0, 0, 0, 0, 0,
            wc.hInstance, None
        )
        if not cls._hwnd:
            raise RuntimeError(f"{cls.__name__}: failed to create hidden window")
        cls._ready.set()
        PumpMessages()

    @classmethod
    def _start(cls) -> None:
        if cls._ready.is_set():
            return
        cls.thread = threading.Thread(target=cls._window_layout_processor_thread, daemon=True, )
        cls.thread.start()
        cls._ready.wait()

    @classmethod
    def resolve(cls, hkl: int) -> str:
        with cls._lock:
            if not cls._hwnd:
                cls._start()

            current_hkl: int = GetKeyboardLayout(cls.thread.native_id or 0)
            if current_hkl == hkl:
                return GetKeyboardLayoutName().lower()

            # noinspection PyTypeChecker
            SendMessage(cls._hwnd, WM_INPUTLANGCHANGEREQUEST, cls.INPUTLANGCHANGE_SYSCHARSET, hkl)
            klid: str = GetKeyboardLayoutName()
            # noinspection PyTypeChecker
            SendMessage(cls._hwnd, WM_INPUTLANGCHANGEREQUEST, cls.INPUTLANGCHANGE_SYSCHARSET, current_hkl)
            return klid.lower()


def main() -> None:
    from win32api import GetKeyboardLayoutList

    for hkl in GetKeyboardLayoutList():
        klid = KlidResolver.resolve(hkl)
        print(f'{hkl = :08x} ({hkl & 0xFFFFFFFF:08x}) • {klid = }')


if __name__ == '__main__':
    main()
