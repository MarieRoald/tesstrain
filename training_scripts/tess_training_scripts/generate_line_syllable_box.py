#!/usr/bin/env python3

import argparse
import io
import unicodedata

from PIL import Image  # type: ignore


def parse_args():
    arg_parser = argparse.ArgumentParser(
        """Creates tesseract box files for given (line) image text pairs"""
    )

    # Text ground truth
    arg_parser.add_argument(
        "-t", "--txt", nargs="?", metavar="TXT", help="Line text (GT)", required=True
    )

    # Image file
    arg_parser.add_argument(
        "-i", "--image", nargs="?", metavar="IMAGE", help="Image file", required=True
    )

    return arg_parser.parse_args()


def main():
    """
    https://stackoverflow.com/questions/6805311/combining-devanagari-characters
    Letters are category Lo (Letter, Other), vowel signs are category Mc
    (Mark, Spacing Combining), virama is category Mn (Mark, Nonspacing) and spaces
    are category Zs (Separator, Space).
    """

    def splitclusters(s):
        """Generate the grapheme clusters for the string s. (Not the full
        Unicode text segmentation algorithm, but probably good enough for
        Devanagari.)

        """
        # http://pyright.blogspot.com/2009/12/pythons-unicodedata-module.html
        # The combining code is typically zero.  The virama gets its own special code of nine.
        # i.e. unicodedata.category=Mn unicodedata.combining=9
        # (Could be used to extend for other Indic languages).

        virama = "\N{DEVANAGARI SIGN VIRAMA}"
        cluster = ""
        last = None
        for c in s:
            cat = unicodedata.category(c)[0]
            if cat == "M" or cat == "L" and last == virama:
                cluster += c
            else:
                if cluster:
                    yield cluster
                cluster = c
            last = c
        if cluster:
            yield cluster

    args = parse_args()
    # Get image size.
    width, height = Image.open(args.image).size

    # load gt
    with io.open(args.txt, "r", encoding="utf-8") as f:
        lines = f.read().strip().split("\n")
        if len(lines) != 1:
            raise ValueError(
                f"ERROR: {args.txt}: Ground truth text file should contain exactly "
                f"one line, not {len(lines)}"
            )
        line = unicodedata.normalize("NFC", lines[0].strip())

    if line:
        for syllable in splitclusters(line):
            print("%s 0 0 %d %d 0" % (syllable, width, height))
            print("\t 0 0 %d %d 0" % (width, height))
