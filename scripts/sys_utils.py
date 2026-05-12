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

import sys


def windows_build():
    v = sys.getwindowsversion()
    return v.major, v.minor, v.build


def supports_msix():
    if sys.platform != "win32":
        return False

    major, minor, build = windows_build()

    return (major > 10) or (major == 10 and build >= 10240)


if __name__ == '__main__':
    print(f'{supports_msix() = }')
