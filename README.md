
# Netrunner Card Extractor

This Python script extracts individual Netrunner cards from PDF files provided by Null Systems Games. The script performs the following tasks:

1. Extracts images from the PDF file.
2. Crops the extracted images to remove margins.
3. Slices the cropped images into individual cards based on a grid.

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
python main.py <pdf_path> <card_pack> <crop> <skip_first>
```

### Arguments:

- `pdf_path`: Path to the PDF file containing the Netrunner cards.
- `card_pack`: Name of the card pack (used in naming the output files).
- `crop`: Number of pixels to crop from each side of the image.
- `skip_first`: Set to `True` to skip processing the first page of the PDF.

### Example:

```bash
python main.py example.pdf "system_gateway" 71 True
```

## Features

1. **Image Extraction**: Extracts images from the PDF using PyMuPDF.
2. **Image Cropping**: Crops the extracted images to remove unnecessary margins.
3. **Card Slicing**: Slices each cropped image into individual cards using a 3x3 grid.

## Output

The script creates the following directory structure:

- `extracted_images`: Contains images extracted from the PDF.
- `cropped_images`: Contains cropped images.
- `sliced_cards`: Contains the final card images.

## Notes

- Ensure the PDF file is compatible with PyMuPDF for proper image extraction.
- Cropping and slicing parameters may need adjustment based on the card layout in the PDF.
- The script will overwrite the `extracted_images` folder if it already exists.

## License

This project is provided as-is for educational and personal use. All card designs and assets are property of Null Systems Games.

## Disclaimer

The script does not modify or redistribute the original PDF. Ensure you have the right to extract content from the PDF before use.
