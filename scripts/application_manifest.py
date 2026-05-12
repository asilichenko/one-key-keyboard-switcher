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

from pathlib import Path

from scripts.build_config import ManifestInfo, BuildPaths

MANIFEST_NAME = "AppxManifest.xml"
MANIFEST_TEMPLATE_PATH: Path = BuildPaths.PACKAGING_MSIX / "AppxManifest-template.xml"


def render_manifest(manifest_info: ManifestInfo, output_path: Path = BuildPaths.BUILD) -> None:
    manifest_text: str = (MANIFEST_TEMPLATE_PATH.read_text()
                          .replace("{{NAME}}", manifest_info.name)
                          .replace("{{PUBLISHER}}", manifest_info.publisher)
                          .replace("{{VERSION}}", manifest_info.version)
                          .replace("{{DISPLAY_NAME}}", manifest_info.display_name)
                          .replace("{{PUBLISHER_DISPLAY_NAME}}", manifest_info.publisher_display_name)
                          .replace("{{EXECUTABLE}}", manifest_info.executable)
                          .replace("{{EXE_DISPLAY_NAME}}", manifest_info.exe_display_name)
                          .replace("{{EXE_DESCRIPTION}}", manifest_info.exe_description))

    (output_path / MANIFEST_NAME).write_text(manifest_text)


if __name__ == '__main__':
    _manifest_info: ManifestInfo = ManifestInfo(
        name="Package Name",
        publisher="Publisher",
        version="1.0.0.0",
        display_name="Display Name",
        publisher_display_name="Publisher Display Name",
        executable="Exe File Name",
        exe_display_name="Exe Display Name",
        exe_description="Exe Description",
    )
    render_manifest(_manifest_info)
