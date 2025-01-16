# Netrunner Card Extractor

This Python script extracts individual Netrunner cards from PDF files provided by Null Systems Games. It supports two types of packs:

1. **Full Packs** (e.g., System Gateway): Contain one image per page that needs cropping and slicing into individual cards.
2. **Booster Packs** (e.g., Midnight Sun Booster): Contain each card as a separate image on the page, requiring only minor cropping.

The script performs the following tasks based on the input type:

- Extracts images from the PDF file.
- Crops the extracted images to remove margins.
- Optionally slices the cropped images into individual cards based on a grid for Full Packs.

## Prerequisites

Before using this script, ensure you have the following installed:

- Python 3.8 or higher
- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/en/latest/)
- [Pillow (PIL)](https://pillow.readthedocs.io/en/stable/)

Install the required dependencies by running:

```bash
pip install pymupdf pillow
```

## Usage

Run the script using the following syntax:

```bash
python main.py -p <pdf_path> -pc <pack_code> [-c <crop_pixels>] [-f <first_image>] [-l <last_image>] [-s <skip_cards>] [-sn <start_number>] [--skip-crop] [--skip-slice]
```

### Arguments:

- `-p, --pdf <pdf_path>`: Path to the PDF file containing the Netrunner cards. (Required)
- `-pc, --pack-code <pack_code>`: NetrunnerDB card pack code. (Required)
- `-c, --crop <crop_pixels>`: Crop size in pixels. Default is 75. (Optional)
- `-f, --first <first_image>`: The first image to process. Default is 1. (Optional)
- `-l, --last <last_image>`: The last image to process. Default is 100. (Optional)
- `-s, --skip <skip_cards>`: A comma-separated list of cards to skip, with no spaces. Default is an empty string. (Optional)
- `-sn, --start-number <start_number>`: The printed number on the first card in the pack. Default is 1. (Optional)
- `--skip-crop`: Skip the crop step. (Optional)
- `--skip-slice`: Skip the slice step. (Optional)

### Example:

#### For a Full Pack:
```bash
python main.py -p example_full_pack.pdf -pc system_gateway -c 71 -f 1 -l 50 --skip-slice
```

#### For a Booster Pack:
```bash
python main.py -p example_booster_pack.pdf -pc midnight_sun -c 20 -f 1 -l 30 --skip-crop
```

## Features

1. **Image Extraction**: Extracts images from the PDF using PyMuPDF.
2. **Image Cropping**: Crops the extracted images to remove unnecessary margins.
3. **Card Slicing (Full Packs)**: Slices each cropped image into individual cards using a 3x3 grid.

## Output

The script creates the following directory structure in the specified output folder:

- `extracted_images`: Contains images extracted from the PDF.
- `cropped_images`: Contains cropped images.
- `sliced_cards` (only for Full Packs): Contains the final card images.

## Notes

- Ensure the PDF file is compatible with PyMuPDF for proper image extraction.
- Cropping and slicing parameters may need adjustment based on the card layout in the PDF.
- The script will overwrite existing output directories if they already exist.
- For Booster Packs, the `sliced_cards` directory will not be created as slicing is not required.

## License

This project is provided as-is for educational and personal use. All card designs and assets are property of Null Systems Games.

## Disclaimer

The script does not modify or redistribute the original PDF. Ensure you have the right to extract content from the PDF before use.

