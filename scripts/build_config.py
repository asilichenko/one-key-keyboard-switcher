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

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import yaml

import onekey_layout_switcher
from scripts import sys_utils


@dataclass(frozen=True)
class BuildPaths:
    ROOT: Path = Path(__file__).parent.parent
    BUILD: Path = ROOT / "build"
    DIST: Path = ROOT / "dist"

    REV_FILE = ROOT / ".build_revision"

    ROOT_MODULE_NAME: str = onekey_layout_switcher.__name__
    ROOT_MODULE: Path = ROOT / ROOT_MODULE_NAME

    PACKAGING_ROOT: Path = ROOT / "packaging"
    PACKAGING_MSIX: Path = PACKAGING_ROOT / "msix"
    PACKAGING_PYINSTALLER: Path = PACKAGING_ROOT / "pyinstaller"

    PYTHON_ASSETS_SOURCE_DIR: str = os.path.join(ROOT_MODULE_NAME, "assets")
    PYTHON_ASSETS_SOURCE: Path = ROOT / PYTHON_ASSETS_SOURCE_DIR

    MSIX_ASSETS_SOURCE_DIR: Path = "Assets"
    MSIX_ASSETS_SOURCE: Path = PACKAGING_MSIX / MSIX_ASSETS_SOURCE_DIR

    APP_ICON_PATH: Path = PACKAGING_PYINSTALLER / "app_icon.ico"
    DPI_AWARE_MANIFEST_PATH: Path = PACKAGING_PYINSTALLER / "dpi_aware.manifest"
    MAIN_PY_PATH: Path = ROOT / "main.py"


@dataclass(frozen=True)
class VersionInfo:
    filevers: tuple
    prodvers: tuple
    product_name: str
    file_description: str
    product_version: str
    legal_copyright: str


@dataclass(frozen=True)
class ManifestInfo:
    name: str
    publisher: str
    display_name: str
    version: str
    publisher_display_name: str
    executable: str
    exe_display_name: str
    exe_description: str


@dataclass
class AppConfig:
    exe_name: str
    exe_display_name: str
    exe_description: str

    @property
    def exe_path(self) -> Path:
        return BuildPaths.DIST / self.exe_name


@dataclass
class Version:
    major: int
    minor: int
    build: int
    revision: int

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.build}.{self.revision}"

    def as_tuple(self):
        return self.major, self.minor, self.build, self.revision


@dataclass
class PackageConfig:
    name: str
    display_name: str
    publisher: str
    publisher_display_name: str


@dataclass
class SigningConfig:
    cert_file: str
    cert_password: str  # з env, не з yaml

    @classmethod
    def from_dict(cls, data: dict) -> SigningConfig:
        password = os.environ.get(data["cert_password"])
        if not password:
            raise EnvironmentError("CERT_PASSWORD environment variable is not set")
        return cls(
            cert_file=data["cert_file"],
            cert_password=password,
        )


@dataclass
class ToolsConfig:
    makeappx: str
    signtool: str

    def __post_init__(self) -> None:
        if not sys_utils.supports_msix():
            return

        for field_name in ("makeappx", "signtool"):
            path: str = getattr(self, field_name)
            if not Path(path).exists():
                raise FileNotFoundError(f"Tool not found: {field_name} = {path}")


@dataclass
class Config:
    app: AppConfig
    version: Version
    package: PackageConfig
    signing: SigningConfig
    tools: ToolsConfig

    @classmethod
    def load(cls, path: Union[str, Path]) -> Config:
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(
            app=AppConfig(**data["app"]),
            version=Version(**data["version"]),
            package=PackageConfig(**data["package"]),
            signing=SigningConfig.from_dict(data["signing"]),
            tools=ToolsConfig(
                makeappx=data["tools"]["makeappx"],
                signtool=data["tools"]["signtool"],
            ),
        )


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()  # читає .env файл

    cfg = Config.load("../config/build_config.yaml")

    print(cfg.package.name)  # Publisher.PackageName
    print(cfg.tools.makeappx)  # Path('C:\Program Files\...')
    print(cfg.signing.cert_password)  # з env, не з файлу
