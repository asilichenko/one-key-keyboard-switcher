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

import shutil
import subprocess
from pathlib import Path

from scripts import application_manifest
from scripts.build_config import ManifestInfo, BuildPaths
from scripts.publisher_hash import calculate_publisher_hash

ARCH = 'x64'
RESOURCE_ID = ''


def prepare_package(*,
                    manifest_info: ManifestInfo,
                    exe_path: Path
                    ) -> Path:
    package_path: Path = BuildPaths.BUILD / manifest_info.name
    if package_path.exists():
        shutil.rmtree(package_path)
    package_path.mkdir(parents=True)

    application_manifest.render_manifest(manifest_info, package_path)

    # copy exe
    shutil.copyfile(
        src=exe_path,
        dst=package_path / manifest_info.executable
    )

    # copy module assets
    shutil.copytree(
        src=BuildPaths.PYTHON_ASSETS_SOURCE,
        dst=package_path / BuildPaths.PYTHON_ASSETS_SOURCE_DIR
    )

    # copy MSIX Assets
    shutil.copytree(
        src=BuildPaths.MSIX_ASSETS_SOURCE,
        dst=package_path / BuildPaths.MSIX_ASSETS_SOURCE_DIR
    )

    return package_path


def create_msix(*,
                make_appx_path_str: str,
                package_path: Path,
                version: str,
                publisher_hash: str) -> Path:
    # [Name]_[Version]_[Architecture]_[ResourceId]_[PublisherHash]
    msix_file_name: str = f'{package_path.name}_{version}_{ARCH}_{RESOURCE_ID}_{publisher_hash}'
    msix_output_path: Path = BuildPaths.DIST / f"{msix_file_name}.msix"

    result = subprocess.run([
        make_appx_path_str,
        "pack",
        "/o",  # overwrite
        "/d", str(package_path),
        "/p", str(msix_output_path)
    ], check=True)

    if result.returncode != 0:
        raise RuntimeError(f"MSIX failed.\n\n{result.stdout}\n{result.stderr}")

    print("✅ build успішно")

    return msix_output_path


def build(*,
          make_appx_path_str: str,
          manifest_info: ManifestInfo,
          exe_path: Path
          ) -> Path:
    print('> building MSIX')

    package_path: Path = prepare_package(
        manifest_info=manifest_info,
        exe_path=exe_path
    )

    pub_hash: str = calculate_publisher_hash(manifest_info.publisher)

    return create_msix(
        make_appx_path_str=make_appx_path_str,
        package_path=package_path,
        version=manifest_info.version,
        publisher_hash=pub_hash
    )


if __name__ == '__main__':
    _make_appx_path_str = r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\MakeAppx.exe"

    _manifest_info: ManifestInfo = ManifestInfo(
        name="Publisher.PackageName",
        publisher="CN=Publisher",
        display_name="Package Display Name",
        version="1.0.0.0",
        publisher_display_name="Publisher Display Name",
        executable="OnekeyLayoutSwitcher.exe",
        exe_display_name="OneKey Layout Switcher",
        exe_description="Helps you to switcher keyboard layout with one key"
    )

    _msix_path: Path = build(
        make_appx_path_str=_make_appx_path_str,
        manifest_info=_manifest_info,
        exe_path=BuildPaths.DIST / _manifest_info.executable
    )

    print(f'MSIX package has been built: {_msix_path}')
