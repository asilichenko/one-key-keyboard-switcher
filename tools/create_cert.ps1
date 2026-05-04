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

do {
    $publisher = Read-Host "Enter value of `Package/Identity/Publisher` (CN=...)"

    if ($publisher -notmatch '^CN=') {
        # CN=01234567-0123-0123-0123-0123456789AB
        Write-Warning "Publisher must start with 'CN='!"
    } else {
        break
    }
} while ($true)

$friendlyName = Read-Host "Enter friendly name (press Enter to skip)"

$outputPath = Read-Host "Enter location to store cert (`$home\Documents\MyCert.pfx)"

do {
    $password = Read-Host "Enter password" -AsSecureString

    # Конвертуємо у plain text для перевірки
    $plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
    )

    if ([string]::IsNullOrWhiteSpace($plainPassword)) {
        Write-Warning "Password cannot be empty! Try again."
    }
} while ([string]::IsNullOrWhiteSpace($plainPassword))


$outputPath = if ($outputPath) { $outputPath } else { "$home\Documents\MyCert.pfx" }

# Створюємо сертифікат
$cert = New-SelfSignedCertificate `
	-Type CodeSigningCert `
	-CertStoreLocation "Cert:\CurrentUser\My" `
	-HashAlgorithm SHA256 `
	-KeyAlgorithm RSA `
	-KeyLength 2048 `
	-Subject $publisher `
    -FriendlyName $friendlyName

# Експортуємо його у файл .pfx
Export-PfxCertificate `
	-Cert $cert `
	-Password $password `
	-FilePath $outputPath

# 🔑 Зберігаємо пароль у файл з розширенням .pwd
$pwdPath = $outputPath + ".pwd"

# Конвертуємо SecureString у plain text
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
)

# Записуємо у файл
Set-Content -Path $pwdPath -Value $plainPassword -NoNewline

Write-Host "`n`n    Password saved to: $pwdPath`n`n"

pause