import fitz
from PIL import Image, ImageOps
import io
import os
import sys
import shutil

cardNumber = 1

try:
    pdf_path = sys.argv[1]
    cardPack = sys.argv[2]
    crop = int(sys.argv[3])
    skipFirst = sys.argv[4] == "True"
except IndexError:
    print("Usage: python main.py <pdf_path> <card_pack> <crop> <skip_first>")
    print("Example: python main.py example.pdf \"system_gateway\" 71 True")
    sys.exit(1)

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
            left = col * card_width + left_offset
            upper = row * card_height + top_offset
            right = left + card_width
            lower = upper + card_height

            card = image.crop((left, upper, right, lower))
            card_path = os.path.join(output_folder, f"{cardPack}_{cardNumber}.png")
            
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
            out_path = os.path.join(output_folder, f"page_{page_index+1}_img_{img_index+1}.png")
            pil_image.save(out_path)
            image_count += 1

    print(f"Extracted {image_count} images to {output_folder}")


def process_pdf_to_cards(pdf_path, output_folder):
    # Step 1: Extract images from the PDF
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    extract_images_via_pixmap(pdf_path, output_folder)


    # Step 2: Crop each extracted image
    cropped_folder = os.path.join(output_folder, "cropped_images")
    os.makedirs(cropped_folder, exist_ok=True)

    bulk_crop_images(output_folder, cropped_folder, left=crop, top=crop, right=crop, bottom=crop)

    # Step 3: Slice each extracted image into cards
    card_folder = os.path.join(output_folder, "sliced_cards")
    os.makedirs(card_folder, exist_ok=True)

    for image_file in os.listdir(cropped_folder):
        if skipFirst and image_file.startswith("page_1"):
            continue
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(cropped_folder, image_file)
            slice_image_to_cards(image_path, card_folder)


# Example usage
# pdf_path = "example.pdf"
output_folder = "extracted_images"
shutil.rmtree(output_folder)


process_pdf_to_cards(pdf_path, output_folder)

