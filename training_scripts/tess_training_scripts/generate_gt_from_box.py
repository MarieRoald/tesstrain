import argparse
import io


def parse_args():
    arg_parser = argparse.ArgumentParser(
        """Creates groundtruth files from text2image generated box files"""
    )

    # Text ground truth
    arg_parser.add_argument(
        "-t", "--txt", nargs="?", metavar="TXT", help="Line text (GT)", required=True
    )

    # Text box file
    arg_parser.add_argument(
        "-b",
        "--box",
        nargs="?",
        metavar="BOX",
        help="text2image generated box file (BOX)",
        required=True,
    )

    return arg_parser.parse_args()


def main():
    #
    # main
    # uses US (ASCII unit separator, U+001F) for substitution to  get the space delimiters
    #
    args = parse_args()
    gtstring = io.StringIO()
    gtfile = open(args.txt, "w", encoding="utf-8")
    with io.open(args.box, "r", encoding="utf-8") as boxfile:
        print(
            "".join(
                line.replace("  ", "\u001f ").split(" ", 1)[0]
                for line in boxfile
                if line
            ),
            file=gtstring,
        )
    gt = gtstring.getvalue().replace("\u001f", " ").replace("\t", "\n")
    print(gt, file=gtfile)
