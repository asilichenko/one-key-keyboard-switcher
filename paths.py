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

# paths.py
import os
import sys
from pathlib import Path
from constants import APP_NAME, ERR_LOG_FILENAME


def get_app_data_folder() -> Path:
    """
    Повертає базову директорію для даних додатка.
    В MSIX це буде: LocalAppData/Packages/<PackageID>/LocalCache/Local/YourApp
    """
    local_app_data = os.getenv('LOCALAPPDATA')
    base_path = Path(local_app_data) / APP_NAME

    return base_path


def get_err_log_file_path() -> Path:
    log_dir = get_app_data_folder() / "logs"
    # Створюємо директорію відразу, якщо її немає
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / ERR_LOG_FILENAME


def get_root_dir() -> str:
    if getattr(sys, 'frozen', False):
        # if run as EXE (PyInstaller)
        application_path: str = os.path.dirname(sys.executable)
    else:
        # if run as script .py
        application_path: str = os.path.dirname(os.path.abspath(__file__))
    return application_path
