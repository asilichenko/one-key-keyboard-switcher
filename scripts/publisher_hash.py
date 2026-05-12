# Based on: https://gist.github.com/marcinotorowski/6a51023600160fcceef9ceea341bbc4a
# Original author: Marcin Otorowski
# Python port: Oleksii Sylichenko (asilichenko), 2026

import hashlib


def calculate_publisher_hash(publisher_id: str) -> str:
    encoded = hashlib.sha256(publisher_id.encode("utf-16-le")).digest()

    binary_string = "".join(f"{b:08b}" for b in encoded[:8]) + "0"  # 65 bits = 13 * 5

    alphabet = "0123456789abcdefghjkmnpqrstvwxyz"
    return "".join(
        alphabet[int(binary_string[i * 5:(i + 1) * 5], 2)]
        for i in range(len(binary_string) // 5)
    )


if __name__ == "__main__":
    test_cases = [
        ("CN=Publisher", "zjr0dfhgjwvde"),
        ("E=marcin@otorowski.com, CN=Marcin Otorowski, O=Marcin Otorowski, S=zachodniopomorskie, C=PL",
         "zxq1da1qqbeze"),
    ]
    for publisher, expected in test_cases:
        result = calculate_publisher_hash(publisher)
        assert result == expected, f"FAIL [{publisher!r}]: expected {expected!r}, got {result!r}"
        print(f"OK: {result}")
