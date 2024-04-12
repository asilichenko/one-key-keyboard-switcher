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

# https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.get
from configparser import ConfigParser

logger = logging.getLogger(__name__)

CONFIG_FILENAME = 'config.ini'

SETTINGS_SECTION = 'Settings'

SETTINGS_RIGHT_CTRL = 'right ctrl'
"""Option name for the language ID to be associated with the right CTRL key press event."""

SETTINGS_RIGHT_SHIFT = 'right shift'
"""Option name for the language ID to be associated with the right SHIFT key press event."""

MIN_FLOAT = 0.1
"""Minimum value for float values. 
If the option value is not empty and is valid, 
then it will be stored as a value no less than this specified value."""

SETTINGS_CHECK_INTERVAL = 'layout check interval'
"""How often layout change should be checked."""

SETTINGS_TIMEOUT = 'key press timeout'
"""If the key is pressed for longer than this specified time in seconds, the layout will not be changed."""


class Config:
    """Reads config from an INI file and stores data into fields."""

    right_ctrl_lang = None
    right_shift_lang = None
    key_press_timeout = None
    layout_check_interval = None

    def __init__(self):
        self._config = ConfigParser()

    def _is_empty(self, section, option):
        """Checks if section or option do not exist."""

        # Check if section exists
        if not self._config.has_section(section):
            logger.error("Section '[%s]' should be present.", section)
            return True

        # Check if option exists
        if not self._config.has_option(section, option):
            logger.error("Option should be present: [%s] -> %s", section, option)
            return True

    def _get_int(self, section, option):
        """
        Reads option value from config section and parses it as integer.
        If any exception happens then return None.
        """

        if self._is_empty(section, option):
            return None

        val = self._config.get(section, option)

        retval = None
        # Parse value as integer
        # noinspection PyBroadException
        try:
            retval = int(val, base=16) if val.startswith('0x') else int(val)
        except Exception:
            logger.error("Option should be integer either in '0xABC' or '123' format: [%s] -> %s = %s",
                         section, option, val)
        finally:
            return retval

    def _get_float(self, section, option):
        """
        Reads option value from config section and parses it as float.
        If any exception happens then return None.
        """

        if self._is_empty(section, option):
            return None

        val = None
        # noinspection PyBroadException
        try:
            val = self._config.getfloat(section, option)
        except Exception:
            raw = self._config.get(section, option)
            logger.error("Option should contain either integer (ABC) or float (AB.C) value: [%s] -> %s = %s",
                         section, option, raw)
        finally:
            return max(val, MIN_FLOAT) if val is not None else None

    def read_ini(self):
        """
        Reads settings from ini file.
        If an option is empty or not valid then its value leaves as None.
        """
        try:
            self._config.read(CONFIG_FILENAME)

            self.right_ctrl_lang = self._get_int(SETTINGS_SECTION, SETTINGS_RIGHT_CTRL)
            self.right_shift_lang = self._get_int(SETTINGS_SECTION, SETTINGS_RIGHT_SHIFT)
            self.key_press_timeout = self._get_float(SETTINGS_SECTION, SETTINGS_TIMEOUT)
            self.layout_check_interval = self._get_float(SETTINGS_SECTION, SETTINGS_CHECK_INTERVAL)
        except Exception as e:
            logger.error("Config read issue: %s", str(e))


if __name__ == "__main__":
    c = Config()
    c.read_ini()
    print("right_ctrl_lang: ", c.right_ctrl_lang)
    print("right_shift_lang: ", c.right_shift_lang)
    print("key_press_timeout: ", c.key_press_timeout)
    print("layout_check_interval: ", c.layout_check_interval)
