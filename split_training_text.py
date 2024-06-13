import os
from pathlib import Path
import subprocess
import argparse
from multiprocessing import Pool, cpu_count
from functools import partial
from itertools import product

def parse_args():
    parser = argparse.ArgumentParser(
        prog="Split traning text",
        description="Generates .tif, .box and .gt.txt files from lines in sme.training_text. Control range of lines with the \"--start\" and \"--end\" parameters."
    )
    parser.add_argument('--start', type=int, help='Starting line count (inclusive)')
    parser.add_argument('--end', type=int, help='Ending line count (exclusive)')
    parser.add_argument('--cores', '-c', type=int, default=cpu_count(), help='Number of cpu cores')
    
    return parser.parse_args()


def import_fonts(font_file):
    with open(font_file, 'r') as f:
        font_list = f.readlines()
    
    return [line.strip() for line in font_list if not line.startswith("#")]


def create_line_images(args, lines, output_directory, training_text_file_name):
    line_index = args[0]
    font_name = args[1]
    
    line = lines[line_index].strip()

    line_serial = f"{line_index:d}"
    font_name_string = font_name.replace(" ", "_")
    
    if not os.path.exists(f"{output_directory}/{font_name_string}"):
        os.mkdir(f"{output_directory}/{font_name_string}")

    file_base_name = f'{training_text_file_name}_{line_serial}_{font_name_string}'
    if (os.path.exists(f"{output_directory}/{font_name_string}/{file_base_name}.gt.txt") and 
        os.path.exists(f"{output_directory}/{font_name_string}/{file_base_name}.tif") and 
        os.path.exists(f"{output_directory}/{font_name_string}/{file_base_name}.box")):
        return

    line_gt_text = os.path.join(output_directory, font_name_string, f'{training_text_file_name}_{line_serial}_{font_name_string}.gt.txt')
    with open(line_gt_text, 'w') as output_file:
        output_file.writelines([line])

    subprocess.run([
        'text2image',
        f'--font={font_name}',
        f'--text={line_gt_text}',
        f'--outputbase={output_directory}/{font_name_string}/{file_base_name}',
        '--max_pages=1',
        '--strip_unrenderable_words=false',
        '--leading=36',
        '--xsize=3600',
        '--ysize=330',
        '--distort_image=true',
        '--invert=false',
        # '--resolution=600',
        # '--char_spacing=1.0',
        '--exposure=0',
        '--unicharset_file=training-data/sme/sme.unicharset',
    ])

def create_training_data(training_text_file, font_list, output_directory, cores, start_line=None, end_line=None):
    with open(training_text_file, 'r') as input_file:
        lines = input_file.readlines()

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    if start_line is None:
        start_line = 0

    if end_line is None:
        end_line = len(lines)

    with Pool(cores) as pool:
        pool.map(
            partial(create_line_images, 
                    lines=lines,
                    output_directory=output_directory, 
                    training_text_file_name=Path(training_text_file).stem), 
            list(product(range(start_line, end_line), font_list)))

    if os.path.exists(f"{output_directory}/fonts.conf"):
        os.remove(f"{output_directory}/fonts.conf")

if __name__ == "__main__":
    args = parse_args()

    training_text_file = 'training-data/sme/sme.training_text'
    output_directory = 'training-data/sme-ground-truth'

    font_file = 'training-data/sme/okfonts.txt'
    font_list = import_fonts(font_file)

    create_training_data(training_text_file, font_list, output_directory, args.cores, args.start, args.end)
