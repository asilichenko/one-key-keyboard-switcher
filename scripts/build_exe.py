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

import os.path
import shutil
import subprocess
from pathlib import Path

from scripts.build_config import BuildPaths, VersionInfo
import onekey_layout_switcher

ROOT: Path = Path(__file__).parent.parent

VERSION_INFO_FILE_NAME: str = 'version_info.txt'
VERSION_INFO_TEMPLATE_PATH: Path = BuildPaths.PACKAGING_PYINSTALLER / f"version_info-template.txt"

SPEC_FILE_NAME: str = 'app.spec'
SPEC_TEMPLATE_PATH: Path = BuildPaths.PACKAGING_PYINSTALLER / "app-template.spec"

ASSETS: str = os.path.join(onekey_layout_switcher.__name__, "assets")


def render_spec(exe_name: str, output_path: Path) -> None:
    spec_text: str = (SPEC_TEMPLATE_PATH.read_text()
                      .replace('{{EXE_NAME}}', exe_name)
                      .replace('{{MAIN_PY}}', str(BuildPaths.MAIN_PY_PATH))
                      .replace('{{ICON}}', str(BuildPaths.APP_ICON_PATH))
                      .replace('{{MANIFEST}}', str(BuildPaths.DPI_AWARE_MANIFEST_PATH)))

    (output_path / SPEC_FILE_NAME).write_text(spec_text)


def render_version_info(version_info: VersionInfo, output_path: Path) -> None:
    version_info_text: str = (VERSION_INFO_TEMPLATE_PATH.read_text()
                              .replace('{{FILEVERS}}', str(version_info.filevers))
                              .replace('{{PRODVERS}}', str(version_info.prodvers))
                              .replace('{{PRODUCT_NAME}}', version_info.product_name)
                              .replace('{{FILE_DESCRIPTION}}', version_info.file_description)
                              .replace('{{PRODUCT_VERSION}}', version_info.product_version)
                              .replace('{{LEGAL_COPYRIGHT}}', version_info.legal_copyright))

    (output_path / VERSION_INFO_FILE_NAME).write_text(version_info_text, encoding='utf8')


def make_exe(build_path: Path, dist_path: Path) -> None:
    subprocess.run([
        'pyinstaller',
        '--clean',  # Clean PyInstaller cache and remove temporary files before building.
        '--workpath=' + str(build_path),
        # Where to put all the temporary work files, .log, .pyz and etc. (default: ./build)
        '--distpath=' + str(dist_path),  # Where to put the bundled app (default: ./dist)
        str(build_path / SPEC_FILE_NAME)
    ])


def build(*,
          exe_name: str,
          version_info: VersionInfo,
          build_path: Path = BuildPaths.BUILD,
          dist_path: Path = BuildPaths.DIST
          ) -> Path:
    print('> building exe')

    render_spec(exe_name, build_path)
    render_version_info(version_info, build_path)

    make_exe(build_path=build_path, dist_path=dist_path)

    # copy assets
    dist_assets = dist_path / ASSETS
    if dist_assets.exists():
        shutil.rmtree(dist_assets)
    shutil.copytree(
        src=ROOT / ASSETS,
        dst=dist_assets,
    )

    return dist_path / exe_name


if __name__ == '__main__':
    BuildPaths.BUILD.mkdir(exist_ok=True)
    BuildPaths.DIST.mkdir(exist_ok=True)

    _exe_name = "OnekeyLayoutSwitcher.exe"

    _version_info: VersionInfo = VersionInfo(
        filevers=(1, 2, 3, 4),
        prodvers=(1, 2, 3, 5),
        product_name="test product name",
        file_description="test file description",
        product_version="test version - 12345",
        legal_copyright="Copyright: Test (test)"
    )

    build(exe_name=_exe_name, version_info=_version_info)
