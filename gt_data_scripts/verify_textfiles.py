import os
import subprocess
from pathlib import Path

def main():
    """
    Program to verify results from pdf_to_training_data.py. 
    Shows the last textline and image for each page. 
    If they match everything should be ok.
    """
    OUTPUT_DIR = Path("output")

    for file in sorted(OUTPUT_DIR.glob("*.txt")):        
        page = file.name[:-10]
        last_line = sorted(OUTPUT_DIR.glob(f"{page}*.txt"))[-1]
        if file == last_line:
            with open(file, "r") as f:
                print(file.name)
                print()
                print(f.read())
                subprocess.run(["feh", f"output/{file.name.replace(".gt.txt", ".png")}"])
                print()
                # input()


if __name__ == "__main__":
    raise SystemExit(main())