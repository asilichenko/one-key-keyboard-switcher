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
from constants import APP_NAME


def show_error_message(text: str) -> None:
    # MessageBoxW для підтримки Unicode (кирилиці)
    MB_OK = 0x00000000
    MB_ICONERROR = 0x00000010
    MB_SETFOREGROUND = 0x00010000  # Змушує вікно стати активним
    MB_TOPMOST = 0x00040000  # Вікно поверх усіх інших

    flags = MB_OK | MB_ICONERROR | MB_SETFOREGROUND | MB_TOPMOST
    ctypes.windll.user32.MessageBoxW(0, text, APP_NAME, flags)


if __name__ == '__main__':
    show_error_message("Не вдалося встановити хук клавіатури.\nПрограма буде закрита.")
