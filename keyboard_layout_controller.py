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
from typing import Optional

import win32gui
import win32api
import win32process

"""WM_INPUTLANGCHANGEREQUEST: Message posted to the window when input language should be changed.
https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-inputlangchangerequest"""
from win32con import WM_INPUTLANGCHANGEREQUEST

INPUTLANGCHANGE_SYSCHARSET: int = 0x0001
"""Flag means: set the new input locale to be the keyboard layout.
https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-inputlangchangerequest
"""


def get_keyboard_layout_id() -> int:
    """Returns keyboard layout ID for the foreground window.

    :return: keyboard layout ID
    :rtype: int
    """

    foreground_window_handle: int = win32gui.GetForegroundWindow()
    thread_id: int = win32process.GetWindowThreadProcessId(foreground_window_handle)[0]
    return win32api.GetKeyboardLayout(thread_id)


def extract_country_id(layout_id: int) -> int:
    """Extracts country ID from the keyboard layout ID.
    :param layout_id: The ID of the keyboard layout.
    :return: The last 16 bits of the layout ID.
    :rtype: int
    """

    return layout_id & (2 ** 16 - 1)


def set_next_layout() -> None:
    """Sets the next (cyclically) layout in the list as the current one."""

    layouts: list = win32api.GetKeyboardLayoutList()
    layout_id: int = get_keyboard_layout_id()

    index: int = layouts.index(layout_id)
    layout_id: int = layouts[(index + 1) % len(layouts)]
    set_layout(layout_id)


def get_parent_window(hwnd: int) -> Optional[int]:
    return win32gui.GetParent(hwnd)


def set_layout(layout_id: int) -> None:
    """Sets the keyboard layout according to either the language ID or the layout ID.
    If a language contains more than one layout, it could be important what you pass to this method
    and what you want to change.

    :param layout_id: Either the keyboard layout ID or the country ID.
    """

    foreground_wnd: int = win32gui.GetForegroundWindow()
    parent_hwnd: int = get_parent_window(foreground_wnd)
    hwnd: int = parent_hwnd if parent_hwnd else foreground_wnd
    """If the foreground window has a parent, 
    then we have to address the request for a keyboard layout change to its parent.
    
    For example:
    
    "Notepad" -> "Save As":
        - "Save as" - is_child = False, is_popup = True
        - "Notepad" - parent window
    
    "Desktop" aka "Program Manager": is_child = False, is_popup = True, parent = 0
    "Start Menu": is_child = False, is_popup = True, parent = 0
    
    To get window title:
        window_title = win32gui.GetWindowText(foreground_wnd)
    """

    win32api.PostMessage(hwnd, WM_INPUTLANGCHANGEREQUEST, INPUTLANGCHANGE_SYSCHARSET, layout_id)
    """Async request for language changing.
    Window may reject language changing.
    
    For sync request, use SendMessage, but note that this call
    does not update the language in the system language panel,
    but you can use it in addition to the PostMessage call."""
