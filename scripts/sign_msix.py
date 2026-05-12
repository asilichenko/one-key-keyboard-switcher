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

import subprocess
import sys

from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

from scripts.build_config import BuildPaths

SIGN_TIMESTAMP_URL = "http://timestamp.digicert.com"


def get_publisher_from_pfx(pfx_path: str, password: str) -> str:
    with open(pfx_path, "rb") as f:
        pfx_data = f.read()

    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        pfx_data,
        password.encode() if password else None,
        default_backend()
    )

    subject = certificate.subject

    # RFC4514 string — це саме той формат, який очікує Windows (CN=Name, O=Org...)
    return subject.rfc4514_string()


def sign_with_signtool(*,
                       signtool_path_str: str,
                       publisher: str,
                       msix_path_str: str,
                       cert_path_str: str,
                       cert_password: str
                       ) -> None:
    """
    Підписання пакета.
    Якщо видає помилку, то можливо Publisher з маніфесту не співпадає з Publisher з сертифікату,
    або сертифікат не було додано до довірених, або було додано до локального користувача, а не комп'ютера
    Перевірити наявність сертифіката - certlm.msc
    Довірені кореневі центри / Certificates /
    """

    print('> signing MSIX')

    cert_publisher: str = get_publisher_from_pfx(cert_path_str, cert_password)
    if publisher != cert_publisher:
        print("❌ ПОМИЛКА: Невідповідність видавця (Publisher Mismatch)!")
        print(f"• MSIX: {publisher}")
        print(f"• PFX:  {cert_publisher}")
        print("Або ви вказали в `build_config.yaml` невірне значення `package.publisher`, "
              "або підписуєте не тим сертифікатом.")
        sys.exit(1)  # Зупиняємо збірку з кодом помилки

    cmd = [
        signtool_path_str, "sign",
        "/fd", "SHA256",
        "/f", cert_path_str,
        "/p", cert_password,
        "/tr", SIGN_TIMESTAMP_URL,
        "/td", "SHA256",
        msix_path_str,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Не вдалося підписати пакет.\n\n{result.stdout}\n{result.stderr}")

    print("✅ Підписано успішно")


if __name__ == '__main__':
    _signtool_path: str = r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\signtool.exe"
    _publisher: str = "CN=Publisher"
    _cert_file: str = r"C:\cert\Publisher.pfx"
    _cert_password: str = "0"

    _package_file_name = "Publisher.PackageName_1.0.0.0_x64__zjr0dfhgjwvde.msix"

    sign_with_signtool(
        signtool_path_str=_signtool_path,
        publisher=_publisher,
        msix_path_str=str(BuildPaths.DIST / _package_file_name),
        cert_path_str=_cert_file,  # .pfx файл
        cert_password=_cert_password
    )
