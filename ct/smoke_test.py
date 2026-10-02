#!/usr/bin/env python3
"""Smoke test for the Cyber Triage build of msiecfexport.

Usage: smoke_test.py <msiecfexport> <sample index.dat>

The sample must be a version 5.2 index.dat with at least one URL record,
such as the one synctestdata downloads into tests/input/public.
"""

import os
import re
import struct
import subprocess
import sys
import tempfile

URL_RECORD = "Record type\t\t: URL"


def run(arguments):
    """Runs msiecfexport and returns its exit code and standard output."""
    result = subprocess.run(arguments, capture_output=True, timeout=120)
    return result.returncode, result.stdout.decode("latin-1")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    msiecfexport, sample = sys.argv[1], sys.argv[2]
    failures = []

    exit_code, _ = run([msiecfexport, "-V"])
    if exit_code != 0:
        failures.append(f"-V exited with {exit_code}")

    exit_code, sample_output = run([msiecfexport, sample])
    number_of_urls = sample_output.count(URL_RECORD)
    print(f"sample: exit code {exit_code}, {number_of_urls} URL records")
    if (
        exit_code != 0
        or "Export completed." not in sample_output
        or number_of_urls == 0
    ):
        failures.append("the sample did not export cleanly")

    exit_code, output = run([msiecfexport, "-m", "all", sample])
    if exit_code != 0 or "Exporting recovered items." not in output:
        failures.append(f"-m all exited with {exit_code} or exported no recovered pass")

    with tempfile.TemporaryDirectory() as directory:
        zeros = os.path.join(directory, "zeros.dat")
        with open(zeros, "wb") as file_object:
            file_object.write(bytes(32768))

        exit_code, _ = run([msiecfexport, zeros])
        print(f"zero-filled file: exit code {exit_code}")
        if exit_code != 1:
            failures.append(f"a zero-filled file exited with {exit_code}, expected 1")

        # Point the location of the first URL record past the end of the record.
        # Upstream msiecfexport stops at that record; this build must skip it and
        # export the rest.
        match = re.search(
            URL_RECORD + r"\r?\nOffset range\t\t: (\d+) - ", sample_output
        )
        if not match:
            failures.append("no URL record offset found in the sample output")
        else:
            with open(sample, "rb") as file_object:
                data = bytearray(file_object.read())
            struct.pack_into("<I", data, int(match.group(1)) + 0x34, 0xFFF0)

            damaged = os.path.join(directory, "damaged.dat")
            with open(damaged, "wb") as file_object:
                file_object.write(data)

            exit_code, damaged_output = run([msiecfexport, damaged])
            damaged_urls = damaged_output.count(URL_RECORD)
            print(
                f"damaged URL record: exit code {exit_code}, {damaged_urls} URL records"
            )
            if (
                exit_code != 0
                or "Unable to retrieve item" not in damaged_output
                or damaged_urls != number_of_urls - 1
            ):
                failures.append(
                    f"a damaged URL record gave {damaged_urls} URL records, "
                    f"expected {number_of_urls - 1} and an 'Unable to retrieve item' line"
                )

    for failure in failures:
        print(f"FAIL: {failure}")
    if not failures:
        print("PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
