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
import os
import shutil
import subprocess
import datetime
import icon_generator

PROJECT_NAME = 'One key layout switcher'
DIST_ROOT = 'dist/'
DIST_PATH = DIST_ROOT + PROJECT_NAME + '/'

ICON = 'icon.gif'
"""Should have the same value in the 'main.spec'

If you use icon in 'png' format (or in 'ico' format but created by pillow lib)
then user's antivirus may recognize your exe file as trojan 'Win64:Evo-Gen'
"""

ICON_TO_COPY = None  # None  # 'icons/keyboard-shortcut.png'  # 'icons/keyboard3.ico'
"""First priority: Copy image file and make an icon from it."""

ICON_COUNTRIES = []  # []  # ['United States', 'Ukraine']
"""Second priority: Generate an icon with flags of two countries."""

EXE_FILENAME = PROJECT_NAME + '.exe'
ARCHIVE_FORMAT = 'zip'
BUILD_DATE = str(datetime.date.today()).replace('-', '')
ARCHIVE_NAME = (DIST_ROOT + PROJECT_NAME + '-' + BUILD_DATE).replace(' ', '_').lower()

RESOURCES = ['flags', 'config.ini']


def setup():
    logging_config()


def logging_config():
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")


def clean():
    logging.info('Clean')

    if os.path.exists(DIST_PATH):
        logging.info('\tRemove dist directory: %s', DIST_PATH)
        shutil.rmtree(DIST_PATH)

    archive_filename = ARCHIVE_NAME + '.' + ARCHIVE_FORMAT
    if os.path.exists(archive_filename):
        logging.info('\tRemove archive: %s', archive_filename)
        os.remove(archive_filename)
    else:
        logging.info('\tArchive does not exist: %s', archive_filename)


def make_icon():
    logging.info("Make icon")

    if ICON_TO_COPY is not None:
        logging.info("\tCopy icon: %s", ICON_TO_COPY)
        icon_generator.copy_icon(ICON_TO_COPY, ICON)
    elif ICON_COUNTRIES is not None and 2 == len(ICON_COUNTRIES):
        logging.info("\tGenerate icon for countries: %s", ICON_COUNTRIES)
        try:
            icon_generator.generate_icon(ICON_COUNTRIES[0], ICON_COUNTRIES[1], ICON)
        except Exception as e:
            logging.exception("Failed to create icon: %s", str(e))
            raise e


def make_exe():
    make_icon()

    logging.info('Make exe file')
    if not os.path.exists(ICON):
        logging.error("\tIcon file must be present: %s", ICON)
        raise FileNotFoundError
    subprocess.run([
        'pyinstaller',
        '--clean',
        '--distpath=' + DIST_PATH,
        'main.spec',
    ])


def copy_resources():
    logging.info('Copy resources')
    for resource in RESOURCES:
        logging.info('\tCopy resource: %s', resource)

        output = DIST_PATH + resource
        if os.path.isdir(resource):
            shutil.copytree(resource, output)
        else:
            shutil.copyfile(resource, output)


def make_archive(archive_format):
    logging.info('Make %s-archive', archive_format)
    shutil.make_archive(
        ARCHIVE_NAME,
        format=archive_format,
        root_dir=DIST_ROOT,
        base_dir=PROJECT_NAME
    )


if __name__ == '__main__':
    setup()
    logging.info('Start building')
    clean()
    make_exe()
    copy_resources()
    make_archive(ARCHIVE_FORMAT)
    logging.info('Finish building')
