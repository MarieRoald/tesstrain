
import cv2
import os.path
import shutil
from pathlib import Path
import subprocess
import argparse

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
TEMP_DIR = Path("temp")

def check_dirs():
    if not os.path.exists(INPUT_DIR):
        os.mkdir(INPUT_DIR)
        print("Please put input PDF file(s) in the \"input\" directory.")
        exit()

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)    
    os.mkdir(TEMP_DIR)

def split_image(image_path, image_name, output_path):

    # Step 1: Load the image
    image = cv2.imread(image_path)

    # Check if the image is None
    if image is None:
        raise ValueError("Invalid image file or path.")

    # Step 2: Preprocess the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # selected a kernel with more width so that we want to connect lines
    kernel_size = (120, 5) # Change this until you get desired results
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)

    # Step 3: Perform the closing operation: Dilate and then close
    bw_closed = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)

    # Desired result is when lines become a complete white block
    # if image_name.endswith("15") or image_name.endswith("38"):
    #     bw_closedS = cv2.resize(bw_closed, (480, 720))
    #     cv2.imshow('bw_closed', bw_closedS)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    # Find contours for each text line
    contours, _ = cv2.findContours(bw_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours to select those whose width is at least 3 times its height
    filtered_contours = [cnt for cnt in contours if (cv2.boundingRect(cnt)[2] / cv2.boundingRect(cnt)[3])>=1.5]

    filtered_contours = [cnt for cnt in filtered_contours if cv2.boundingRect(cnt)[3] > 20]


    # Sort contours based on y-coordinate
    sorted_contours = sorted(filtered_contours, key=lambda contour: cv2.boundingRect(contour)[1])

    padding=3 # can be tweaked
    for i, contour in enumerate(sorted_contours, 1):
        x, y, w, h = cv2.boundingRect(contour)
        x, y, w, h = (x-padding, y-padding, w+(padding*2), h+(padding*2)) 
        if cv2.boundingRect(contour)[3] < 30:
            print(f"{image_name}-{i}")
        # Uncomment to see contours
        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Recognize each line. Crop the image for each line save in "lines" folder.
        line_image = image[y:y + h, x:x+w]
        if line_image.size:
            cv2.imwrite(f'{output_path}/{image_name}-{"%02d" % i}.png',line_image)
        

    # cv2.imshow('Text Lines', image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    # cv2.imwrite('opencv_detect_text_lines.jpg', image)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="PDF to ground truth",
        description="Turns a PDF file into PNGs of text lines with a corresponing .txt file. For use as ground truth data to Tesseract OCR."
    )
    # parser.add_argument("filename", type=str, nargs=1, help="PDF file to be parsed")

    return parser.parse_args()

def main():

    args = parse_args()

    check_dirs()

    for file in INPUT_DIR.glob("*.pdf"):
        name = file.stem
        print(name)
        
        print("\tCreating .png files")
        subprocess.run(["pdftoppm", file, TEMP_DIR / name, "-png", "-gray", "-r", "300"])
        
        print("\tSplitting lines in .png files")
        for image_file in TEMP_DIR.glob(f"{name}*"):
            split_image(str(image_file), image_file.stem, OUTPUT_DIR)

        
        print("\tCreating .gt.txt files")
        subprocess.run(["pdftotext", file, TEMP_DIR / f"{name}.txt", "-raw"])
        
        with open(TEMP_DIR / (name + ".txt"), "r") as f:
            charachter_set = set()
            p = 1
            l = 1
            for line in f.readlines():
                if line.startswith("\x0c"):
                    p += 1
                    l = 1
                
                line = line.strip()

                if line == "":
                    continue

                with open(OUTPUT_DIR / f"{name}-{"%02d" % p}-{"%02d" % l}.gt.txt", "w") as output_file:
                    output_file.write(line)
                    charachter_set.update(line)
                l += 1
        
            print("Unique charachters in text:")
            print(" ".join(sorted(charachter_set)))

    # shutil.rmtree(TEMP_DIR)

    # return 1

if __name__ == "__main__":
    raise SystemExit(main())