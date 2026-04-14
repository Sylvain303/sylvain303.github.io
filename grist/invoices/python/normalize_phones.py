"""
normalize_phones.py
-------------------
Normalizes raw French phone number text into serialized JSON.

Pipeline:
  1. clean_raw(text)  – replace every non-alphanumeric char with a single space.
  2. Split on '\\n'   – each line is one independent record.
  3. Iterative regex  – repeatedly extract (initials, 5×2-digit chunks) until the
                        line is exhausted, or raise PhoneParsingError on remainder.

Design note on bare numbers (no initials):
  The spec requires Group 1 to be one-or-more letters, so a line like
  "06 12 34 45 75" (no initials) will never match and raises PhoneParsingError.
  This is intentional: initials are mandatory to identify the record owner.
"""

import json
import re


class PhoneParsingError(ValueError):
    """Raised when a non-empty line segment cannot be matched by the phone pattern."""


class PhoneNormalizer:
    """
    Normalizes raw French phone number text into serialized JSON.

    Usage:
        normalizer = PhoneNormalizer()
        json_str = normalizer.normalize("JD 06 12 34 45 75")
    """

    _PHONE_RE = re.compile(
        r'([A-Za-z]+)\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})\s+(\d{2})'
    )

    def clean_raw(self, text: str) -> str:
        """Step 1 – replace every non-alphanumeric character with a single space."""
        return re.sub(r'[^A-Za-z0-9]', ' ', text)

    def _parse_line(self, line: str) -> list[dict]:
        """Iteratively extract all (initials, phone) pairs from a single cleaned line."""
        results = []
        remaining = line

        while True:
            remaining = remaining.strip()
            if not remaining:
                break

            m = self._PHONE_RE.search(remaining)
            if m:
                initials = m.group(1).upper()
                phone = ''.join(m.group(i) for i in range(2, 7))
                results.append({"initials": initials, "phone": phone})
                remaining = remaining[:m.start()] + remaining[m.end():]
            else:
                raise PhoneParsingError(
                    f"Cannot parse remainder: {remaining!r}"
                )

        return results

    def normalize(self, raw_text: str, indent: int = 2) -> str:
        """
        Normalize raw French phone number text into a JSON string.

        Parameters
        ----------
        raw_text : str
            Raw input that may contain initials and French phone numbers.
        indent : int
            JSON indentation level (default 2).

        Returns
        -------
        str
            JSON-serialized list of {"initials": ..., "phone": ...} dicts.

        Raises
        ------
        PhoneParsingError
            If any non-empty line segment cannot be matched.
        """
        cleaned = self.clean_raw(raw_text)
        lines = cleaned.split('\n')
        results = []
        for line in lines:
            results.extend(self._parse_line(line))
        return json.dumps(results, indent=indent, ensure_ascii=False)


def normalize_phones(raw_text: str, indent: int = 2) -> str:
    """Module-level convenience wrapper around PhoneNormalizer.normalize()."""
    return PhoneNormalizer().normalize(raw_text, indent=indent)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    normalizer = PhoneNormalizer()

    def run(label: str, raw: str, expect_error: bool = False) -> None:
        print(f"--- {label} ---")
        print(f"Input: {raw!r}")
        try:
            result = normalizer.normalize(raw)
            if expect_error:
                print("FAIL – expected PhoneParsingError but got none.")
                sys.exit(1)
            print(f"Output:\n{result}")
        except PhoneParsingError as e:
            if expect_error:
                print(f"OK – PhoneParsingError raised: {e}")
            else:
                print(f"FAIL – unexpected PhoneParsingError: {e}")
                sys.exit(1)
        print()

    # 1. No initials – must raise PhoneParsingError (initials are mandatory).
    run(
        "bare number, no initials",
        "06 12 34 45 75",
        expect_error=True,
    )

    # 2. Two records on separate lines.
    run(
        "two records on separate lines",
        "X 06 12 34 45 75\nY 06 02 34 45 34",
    )

    # 3. Two matches on the same line.
    run(
        "two matches on the same line",
        "JD 06 12 34 45 75 M 07 98 76 54 32",
    )

    # 4. Unparseable remainder – must raise PhoneParsingError.
    run(
        "unparseable remainder",
        "AB 06 12 34 45 75 GARBAGE",
        expect_error=True,
    )

    # 5. Punctuation separators and multi-letter initials.
    run(
        "punctuation separators, multi-letter initials",
        "MLD: 06.78.90.12.34 / JR: 07-11-22-33-44",
    )
