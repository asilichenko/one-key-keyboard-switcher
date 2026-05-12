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

try:
    GetCurrentPackageFamilyName = kernel32.GetCurrentPackageFamilyName
except AttributeError:
    GetCurrentPackageFamilyName = None


def make_lcid(hkl_or_klid: str | int) -> int | None:
    """
    Make LCID from HKL or KLID.
    :param hkl_or_klid: HKL as int or KLID as str
    :return: int or None if ID does not contain language info
    @see LANGID: https://learn.microsoft.com/en-us/windows/win32/msi/localizing-the-error-and-actiontext-tables
    """
    lang_id: int = (int(hkl_or_klid, 16) if isinstance(hkl_or_klid, str) else hkl_or_klid) & 0xFFFF

    LANG_UNDEFINED: int = 0x0c00
    if lang_id == LANG_UNDEFINED:
        return None

    SORT_DEFAULT: int = 0x0000
    sort: int = SORT_DEFAULT
    return (sort << 16) | lang_id


def lcid_to_locale_name(lcid: int) -> str | None:
    """Converts LCID (int) to Locale Name (str) using Windows API."""

    # Define necessary constants
    LOCALE_NAME_MAX_LENGTH = 85

    # Prepare buffer for result
    buffer = ctypes.create_unicode_buffer(LOCALE_NAME_MAX_LENGTH)

    # Call LCIDToLocaleName
    result = kernel32.LCIDToLocaleName(lcid, buffer, LOCALE_NAME_MAX_LENGTH, 0)

    if result == 0:
        return None

    return buffer.value


def get_locale_info_ex(locale_name: str | None, lc_type: int) -> str | None:
    """https://learn.microsoft.com/en-us/windows/win32/api/winnls/nf-winnls-getlocaleinfoex
    https://learn.microsoft.com/en-us/windows/win32/intl/locale-information-constants"""
    if locale_name is None:
        return None

    # 1. Call once with lpLCData=None to get necessary buffer size
    buf_size: int = kernel32.GetLocaleInfoEx(locale_name, lc_type, None, 0)

    if buf_size == 0:
        return None

    # 2. Prepare buffer and call again
    buf = ctypes.create_unicode_buffer(buf_size)
    result_size: int = kernel32.GetLocaleInfoEx(locale_name, lc_type, buf, buf_size)

    return buf.value if result_size > 0 else None


def get_iso_country_code(locale_name: str) -> str | None:
    return get_locale_info_ex(locale_name, LOCALE_SISO3166CTRYNAME)


def get_country_name(locale_name: str) -> str | None:
    return get_locale_info_ex(locale_name, LOCALE_SENGLISHCOUNTRYNAME)


def is_msix_package() -> bool:
    """Повертає True якщо застосунок запущено з MSIX пакету."""
    if GetCurrentPackageFamilyName is None:
        return False
    buf_len = ctypes.c_uint32(0)
    # noinspection PyCallingNonCallable
    ret = GetCurrentPackageFamilyName(ctypes.byref(buf_len), None)
    return ret in (0, ERROR_INSUFFICIENT_BUFFER)
