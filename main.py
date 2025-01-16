import fitz
from PIL import Image, ImageOps
import io
import os
import sys
import shutil
import requests
import argparse
import json

parser = argparse.ArgumentParser(
    prog='Null Systems Games Netrunner Card Extractor',
    description='Extracts cards from a Netrunner Print and Play PDF',
    epilog='Keep Running!')


parser.add_argument('-p', '--pdf', help='Path to the PDF file (Required)', required=True)
parser.add_argument('-pc', '--pack-code', help='NetrunnerDB card pack code (Required)', required=True)
parser.add_argument('-c', '--crop', help='Crop size in pixels', type=int, default=75, required=False)
parser.add_argument('-f', '--first', help='The first image', default=1, required=False)
parser.add_argument('-l', '--last', help='The last image', default=100, required=False)
parser.add_argument('-s', '--skip', help='A list of cards (comma separated with no spaces)', default="", required=False)
parser.add_argument('-sn', '--start-number', help='The printed number on the first card in the pack', default=1, required=False)
parser.add_argument('-sc', '--skip-crop', help='Skip the crop step', action='store_true', default=False, required=False)
parser.add_argument('-ss', '--skip-slice', help='Skip the slice step', action='store_true', default=False, required=False)


args = parser.parse_args()

pdf_path = args.pdf
cardPack = args.pack_code
crop = args.crop
first = int(args.first)
last = int(args.last)
startNumber = int(args.start_number)
skipCrop = args.skip_crop
skipSlice = args.skip_slice
skipList = args.skip.split(",") if args.skip else []

print(args)


cardNumber = startNumber
pack_list = []


def get_pack_cards(cardPack):
    url = f"https://netrunnerdb.com/api/2.0/public/cards?pack_code={cardPack}"
    response = requests.get(url)
    data = response.json()
    # save the data to a file
    with open("cards.json", "w") as f:
        f.write(json.dumps(data, indent = 4))
    return data["data"]

def get_card_by_code(position):
    # result = [card for card in pack_list if card["position"] == position]
    result = next((card for card in pack_list if card["pack_code"] == cardPack and card["position"] == position), None)
    return result



def bulk_crop_images(input_folder, output_folder, 
                     left=71, top=71, right=71, bottom=71):
    """
    Crops all images in input_folder by the given margins and saves 
    them to output_folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
            input_path = os.path.join(input_folder, filename)
            image = Image.open(input_path)
            width, height = image.size
            
            # Compute new box (left, upper, right, lower)
            crop_box = (
                left,
                top,
                width - right,
                height - bottom
            )
            
            cropped_image = image.crop(crop_box)
            
            output_path = os.path.join(output_folder, filename)
            cropped_image.save(output_path)
            print(f"Cropped and saved {output_path}")


def slice_image_to_cards(image_path, output_folder, grid=(3, 3), bleed_offset=(0, 0)):
    global cardNumber
    # Open the image
    image = Image.open(image_path)
    print(image_path)

    img_width, img_height = image.size
    top_offset, left_offset = bleed_offset

    # Calculate card dimensions
    grid_rows, grid_cols = grid
    card_width = (img_width - left_offset) // grid_cols
    card_height = (img_height - top_offset) // grid_rows

    # Slice the image into cards
    for row in range(grid_rows):
        for col in range(grid_cols):
            if cardNumber < first or cardNumber in skipList or cardNumber > last:
                cardNumber += 1
                continue

            left = col * card_width + left_offset
            upper = row * card_height + top_offset
            right = left + card_width
            lower = upper + card_height

            card = image.crop((left, upper, right, lower))

            card_details = get_card_by_code(cardNumber)

            card_path = os.path.join(output_folder, f"{card_details["code"]}.png")
            
            # Save the card
            card.save(card_path)
            cardNumber += 1
            print(f"Saved card: {card_path}")

def extract_images_via_pixmap(pdf_path, output_folder):
    doc = fitz.open(pdf_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_count = 0
    for page_index, page in enumerate(doc):
        # get_images() returns a list of (xref, ..., width, height, bpc, colorspace, ...)
        for img_index, img_info in enumerate(page.get_images(full=True)):
            xref = img_info[0]
            # Create Pixmap in RGB
            pix = fitz.Pixmap(doc, xref)
            
            # If pix.n >= 4, it has alpha or is CMYK. Convert to plain RGB.
            if pix.n >= 4:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            
            # Convert the pixmap to bytes and open with PIL
            img_data = pix.tobytes("ppm")  # or "png"
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Save with a proper file name
            out_path = os.path.join(output_folder, f"img_{f"{image_count:05}"}.png")
            pil_image.save(out_path)
            image_count += 1

    print(f"Extracted {image_count} images to {output_folder}")


def process_pdf_to_cards(pdf_path, output_folder):
    global cardNumber
    # Step 1: Extract images from the PDF
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    extract_images_via_pixmap(pdf_path, output_folder)

    if not skipCrop:
        # Step 2: Crop each extracted image
        cropped_folder = os.path.join(output_folder, "cropped_images")
        os.makedirs(cropped_folder, exist_ok=True)

        bulk_crop_images(output_folder, cropped_folder, left=crop, top=crop, right=crop, bottom=crop)

    # Step 3: Slice each extracted image into cards
    card_folder = os.path.join("sliced_cards", cardPack)
    os.makedirs(card_folder, exist_ok=True)

    if skipSlice:
        imageCount = startNumber - 1
        # Copy the extracted images to the card folder (skip slicing)
        input_dir = output_folder if skipCrop else cropped_folder

        for image_file in os.listdir(input_dir):
            if imageCount < first or imageCount in skipList or imageCount > last:
                pass
            elif image_file.lower().endswith(('.png', '.jpg', '.jpeg')):

                image_path = os.path.join(input_dir, image_file)

                card_details = get_card_by_code(cardNumber)

                card_path = os.path.join(card_folder, f"{card_details["code"]}.png")

                shutil.copy(image_path, card_path)
                cardNumber += 1

            imageCount += 1
    else: 
        imageCount = 0
        for image_file in os.listdir(cropped_folder):
            if imageCount < first:
                pass
            elif image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(cropped_folder, image_file)
                slice_image_to_cards(image_path, card_folder)
        
            imageCount += 1


# Example usage
# pdf_path = "example.pdf"

pack_list = get_pack_cards(cardPack)

output_folder = "extracted_images"
shutil.rmtree(output_folder)


process_pdf_to_cards(pdf_path, output_folder)

