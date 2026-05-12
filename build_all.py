#  Original code under MIT License
#
#  Copyright (c) 2026 Oleksii Sylichenko
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
# This file is part of a GPL-licensed project.

import datetime
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Union, Callable

from dotenv import load_dotenv

from scripts import (
    build_exe as build_exe_py,
    build_msix as build_msix_py,
    sign_msix as sign_msix_py
)
from scripts.build_config import Config, BuildPaths, VersionInfo, ManifestInfo

BUILD_CONFIG = "config/build_config.yaml"

commands = {}


def load_config(path: Union[str, Path] = BUILD_CONFIG) -> Config:
    print('> load config')

    load_dotenv()  # читає .env файл

    return Config.load(path)


def run(cmd):
    print(f"> {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def command(fn: Callable) -> Callable:
    commands[fn.__name__] = fn
    return fn


@command
def clean():
    print('> clean all')

    build_path: Path = BuildPaths.BUILD
    dist_path: Path = BuildPaths.DIST

    if build_path.exists():
        shutil.rmtree(build_path)

    if dist_path.exists():
        shutil.rmtree(dist_path)

    build_path.mkdir()
    dist_path.mkdir()


def get_and_update_revision(rev_file: Path) -> int:
    """Читає ревізію, інкрементує та зберігає."""
    rev = 0
    if rev_file.exists():
        try:
            rev = int(rev_file.read_text().strip())
        except ValueError:
            rev = 0

    new_rev = rev + 1
    rev_file.write_text(str(new_rev))

    return rev


@command
def build_exe(config: Config = None) -> None:
    if config is None:
        config = load_config()

    year: int = datetime.datetime.now().year
    author: str = config.package.publisher_display_name

    version_info: VersionInfo = VersionInfo(
        filevers=config.version.as_tuple(),
        prodvers=config.version.as_tuple(),
        product_name=config.package.display_name,
        file_description=config.app.exe_description,
        product_version=str(config.version),
        legal_copyright=f"© {year} {author}. All rights reserved."
    )

    build_exe_py.build(
        exe_name=config.app.exe_name,
        version_info=version_info
    )


def build_msix(config: Config = None) -> Path:
    if config is None:
        config = load_config()

    manifest_info: ManifestInfo = ManifestInfo(
        name=config.package.name,
        publisher=config.package.publisher,
        display_name=config.package.display_name,
        version=str(config.version),
        publisher_display_name=config.package.publisher_display_name,
        executable=config.app.exe_name,
        exe_display_name=config.app.exe_display_name,
        exe_description=config.app.exe_description
    )

    return build_msix_py.build(
        make_appx_path_str=config.tools.makeappx,
        manifest_info=manifest_info,
        exe_path=config.app.exe_path
    )


def sign_msix(msix_path: Path, config: Config = None):
    if config is None:
        config = load_config()

    sign_msix_py.sign_with_signtool(
        signtool_path_str=config.tools.signtool,
        publisher=config.package.publisher,
        msix_path_str=str(msix_path),
        cert_path_str=config.signing.cert_file,
        cert_password=config.signing.cert_password
    )


@command
def build_clean():
    clean()
    build()


@command
def build():
    config: Config = load_config()
    config.version.revision = get_and_update_revision(BuildPaths.REV_FILE)

    build_exe(config)
    msix_path: Path = build_msix(config)
    sign_msix(msix_path, config)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        build_clean()
    else:
        command = sys.argv[1]

        if command in commands:
            commands[command]()
        else:
            print(f"Usage: build_all.py [{'|'.join([fn_name for fn_name in commands.keys()])}]")
            sys.exit(1)
