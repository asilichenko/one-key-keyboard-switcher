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
from typing import Optional

import keyboard_layout_controller

# Define constants
LOCALE_USER_DEFAULT = 0x0400
LOCALE_SDECIMAL = 0x0000000E  # Decimal separator string

LOCALE_SISO3166CTRYNAME: int = 0x5A
"""Двобуквений ISO 3166-1 alpha-2 код країни"""

LOCALE_SENGLISHCOUNTRYNAME: int = 0x1002
"""Constant to obtain english name of the country/region, for example, Germany for Deutschland.
https://learn.microsoft.com/en-us/windows/win32/intl/locale-senglish-constants"""

ERROR_INSUFFICIENT_BUFFER = 122

# Setup kernel32 functions
kernel32: ctypes.WinDLL = ctypes.windll.kernel32

GetLocaleInfoW = kernel32.GetLocaleInfoW
GetCurrentPackageFamilyName = kernel32.GetCurrentPackageFamilyName


def get_locale_info(locale, lc_type):
    # 1. Call once with lpLCData=None to get necessary buffer size
    size = GetLocaleInfoW(locale, lc_type, None, 0)
    if size == 0:
        return None

    # 2. Prepare buffer and call again
    buffer = ctypes.create_unicode_buffer(size)
    result = GetLocaleInfoW(locale, lc_type, buffer, size)

    if result > 0:
        return buffer.value
    return None


def get_country_code(country_id) -> Optional[str]:
    return get_locale_info(country_id, LOCALE_SISO3166CTRYNAME)


def is_msix_package() -> bool:
    """Повертає True якщо застосунок запущено з MSIX пакету."""
    buf_len = ctypes.c_uint32(0)
    ret = GetCurrentPackageFamilyName(ctypes.byref(buf_len), None)
    return ret in (0, ERROR_INSUFFICIENT_BUFFER)


if __name__ == '__main__':
    _country_id: int = keyboard_layout_controller.get_country_id()
    _country_code = get_country_code(_country_id)
    print(f'\nCurrent layout country code = {_country_code}')
