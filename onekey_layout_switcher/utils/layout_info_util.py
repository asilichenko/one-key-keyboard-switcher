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

from onekey_layout_switcher.models import LayoutInfo
from onekey_layout_switcher.utils import winapi_utils
from onekey_layout_switcher.utils.klid_resolver import KlidResolver


class LayoutInfoUtil:
    def __init__(self, klid_resolver: KlidResolver) -> None:
        self.klid_resolver = klid_resolver

    def from_hkl(self, hkl: int) -> LayoutInfo:
        """
        Using KlidResolver to obtain KLID of the passed HKL.
        Using winapi utils to make LCID either from KLID or HKL.
        At lease one LCID must be made: LCID from KLID may not exist, but from HKL always.
        Using winapi utils obtain locale by LCID.
        :param hkl: HKL of the loaded keyboard.
        :return: Locale name (optional).
        """
        klid: str = self.klid_resolver.resolve(hkl)
        lcid: int | None = winapi_utils.make_lcid(klid) or winapi_utils.make_lcid(hkl)
        if not lcid:
            raise RuntimeError(f'Failed to obtain LCID from: {hkl = }; {klid = }')

        locale_name: str | None = winapi_utils.lcid_to_locale_name(lcid)
        country_code: str | None = winapi_utils.get_iso_country_code(locale_name) if locale_name else None

        return LayoutInfo(
            hkl=hkl,
            klid=klid,
            locale_name=locale_name,
            country_code=country_code
        )
