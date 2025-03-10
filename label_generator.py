import tempfile
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import os
from zebrafy import ZebrafyImage



def generate_codes(qr_data, barcode_data=None):
    """Generate a QR code and optionally a barcode, and return their file paths."""
    qr_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    qr_file = qr_temp.name

    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_img.save(qr_file)

    barcode_file = None
    if barcode_data:  # Only generate barcode if data is provided
        barcode_temp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        barcode_file = barcode_temp.name

        # Generate Barcode
        barcode_class = barcode.get_barcode_class('code128')
        code128 = barcode_class(barcode_data, writer=ImageWriter())
        code128.save(barcode_file[:-4], options={"write_text": False})

    return qr_file, barcode_file


def create_1x2_product_label(
    qr_data,
    barcode_data=None,
    description="",
    bin_location="",
    product_code="",
    title=""
):
    """Create a 1x2 product label."""
    dpi = 203
    label_width_px = int(2 * dpi)  # 1x2 label
    label_height_px = int(1 * dpi)

    # Generate QR and optionally barcode
    qr_file, barcode_file = generate_codes(qr_data, barcode_data)

    # Create label template
    label = Image.new("RGB", (label_width_px, label_height_px), "white")
    draw = ImageDraw.Draw(label)

    # Add Title
    font_title = ImageFont.truetype("Helvetica", size=int(0.1 * label_height_px))
    title_x = (label_width_px - draw.textlength(title, font=font_title)) / 2
    draw.text((title_x, int(label_height_px * 0.05)), title, fill="black", font=font_title)

    # Add QR Code
    qr_img = Image.open(qr_file)
    qr_width = int(label_height_px * 0.5)
    qr_img = qr_img.resize((qr_width, qr_width))
    qr_x = int(label_width_px * 0.05)
    qr_y = int(label_height_px * 0.15)
    label.paste(qr_img, (qr_x, qr_y))

    # Add Bin Location (below QR code)
    font_bin = ImageFont.truetype("Helvetica", size=int(0.08 * label_height_px))
    max_bin_line_length = 18  # Max characters before wrapping
    wrapped_bin_lines = [bin_location[i:i + max_bin_line_length] for i in range(0, len(bin_location), max_bin_line_length)]
    bin_x = qr_x
    bin_y = qr_y + qr_width + 2
    for i, line in enumerate(wrapped_bin_lines):
        draw.text((bin_x, bin_y + i * (font_bin.size + 2)), line, fill="black", font=font_bin)

    # Add Barcode if exists
    if barcode_file:
        barcode_img = Image.open(barcode_file)
        barcode_width = int(label_width_px * 0.45)
        barcode_height = int(label_height_px * 0.3)
        barcode_img = barcode_img.resize((barcode_width, barcode_height))
        barcode_x = int(label_width_px * 0.55)
        barcode_y = int(label_height_px * 0.2)
        label.paste(barcode_img, (barcode_x, barcode_y))

        # Add Barcode Text
        font_barcode_text = ImageFont.truetype("Helvetica", size=int(0.08 * label_height_px))
        text_width = draw.textlength(product_code, font=font_barcode_text)
        text_x = barcode_x + (barcode_width - text_width) / 2
        text_y = barcode_y + barcode_height + 5
        draw.text((text_x, text_y), product_code, fill="black", font=font_barcode_text)

    # Add Description (with wrapping below Barcode Text, flush-aligned)
    font_desc = ImageFont.truetype("Helvetica", size=int(0.08 * label_height_px))
    max_desc_line_length = 20
    wrapped_desc_lines = [description[i:i + max_desc_line_length] for i in range(0, len(description), max_desc_line_length)]
    desc_x = barcode_x if barcode_file else qr_x
    desc_y = label_height_px * 0.625
    for i, line in enumerate(wrapped_desc_lines):
        draw.text((desc_x, desc_y + i * (font_desc.size + 2)), line, fill="black", font=font_desc)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_path = temp_file.name
        label.save(temp_path, dpi=(dpi, dpi))

    # Cleanup temp QR and barcode files
    os.remove(qr_file)
    if barcode_file:
        os.remove(barcode_file)

    return temp_path

def create_1x3_product_label(
    qr_data,
    barcode_data=None,
    description="",
    bin_location="",
    product_code="",
    title=""
):
    """Create a 1x3 product label."""
    dpi = 203
    label_width_px = int(3 * dpi)  # 1x3 label
    label_height_px = int(1 * dpi)

    # Generate QR and optionally barcode
    qr_file, barcode_file = generate_codes(qr_data, barcode_data)

    # Create label template
    label = Image.new("RGB", (label_width_px, label_height_px), "white")
    draw = ImageDraw.Draw(label)

    # Add Title (Top Center, Smaller Font)
    font_title = ImageFont.truetype("Helvetica", size=int(0.1 * label_height_px))
    title_x = (label_width_px - draw.textlength(title, font=font_title)) / 2
    draw.text((title_x, int(label_height_px * 0.05)), title, fill="black", font=font_title)

    # Add QR Code (Larger Size)
    qr_img = Image.open(qr_file)
    qr_width = int(label_height_px * 0.5)  # QR code size
    qr_img = qr_img.resize((qr_width, qr_width))
    qr_x = int(label_width_px * 0.05)
    qr_y = int(label_height_px * 0.15)  # Adjust vertical position
    label.paste(qr_img, (qr_x, qr_y))

    # Add Bin Location (below QR code)
    font_bin = ImageFont.truetype("Helvetica", size=int(0.09 * label_height_px))  # Bin location text size
    max_bin_line_length = 22  # Max characters before wrapping
    wrapped_bin_lines = [bin_location[i:i + max_bin_line_length] for i in range(0, len(bin_location), max_bin_line_length)]
    bin_x = qr_x
    bin_y = qr_y + qr_width + 5
    for i, line in enumerate(wrapped_bin_lines):
        draw.text((bin_x, bin_y + i * (font_bin.size + 2)), line, fill="black", font=font_bin)

    # Add Barcode if exists
    if barcode_file:
        barcode_img = Image.open(barcode_file)
        barcode_width = int(label_width_px * 0.4)
        barcode_height = int(label_height_px * 0.3)
        barcode_img = barcode_img.resize((barcode_width, barcode_height))
        barcode_x = int(label_width_px * 0.55)
        barcode_y = int(label_height_px * 0.2)
        label.paste(barcode_img, (barcode_x, barcode_y))

        # Add Barcode Text
        font_barcode_text = ImageFont.truetype("Helvetica", size=int(0.08 * label_height_px))
        text_width = draw.textlength(product_code, font=font_barcode_text)
        text_x = barcode_x + (barcode_width - text_width) / 2
        text_y = barcode_y + barcode_height + 5
        draw.text((text_x, text_y), product_code, fill="black", font=font_barcode_text)

    # Add Description (with wrapping below Barcode Text, flush-aligned)
    font_desc = ImageFont.truetype("Helvetica", size=int(0.08 * label_height_px))
    max_desc_line_length = 32  # Characters per line before wrapping
    wrapped_desc_lines = [description[i:i + max_desc_line_length] for i in range(0, len(description), max_desc_line_length)]
    desc_x = barcode_x if barcode_file else qr_x
    desc_y = label_height_px * 0.625
    for i, line in enumerate(wrapped_desc_lines):
        draw.text((desc_x, desc_y + i * (font_desc.size + 2)), line, fill="black", font=font_desc)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_path = temp_file.name
        label.save(temp_path, dpi=(dpi, dpi))

    # Cleanup temp QR and barcode files
    os.remove(qr_file)
    if barcode_file:
        os.remove(barcode_file)

    return temp_path


def create_2x4_shelf_label(bin_location, title):
    """Generate a 2x4 shelf label with the Bin #: QR code and save it to a temporary file."""
    dpi = 203
    label_width_px = int(4 * dpi)  # 4 inches wide
    label_height_px = int(2 * dpi)  # 2 inches tall

    # Generate QR Code for Bin #
    qr_file, _ = generate_codes(bin_location, None)  # Only QR code is generated, no barcode

    # Create label template
    label = Image.new("RGB", (label_width_px, label_height_px), "white")
    draw = ImageDraw.Draw(label)

    # Add Title (Top Center)
    font_title = ImageFont.truetype("Helvetica", size=int(0.1 * label_height_px))
    title_x = (label_width_px - draw.textlength(title, font=font_title)) / 2
    draw.text((title_x, int(label_height_px * 0.03)), title, fill="black", font=font_title)

    # Add QR Code
    qr_img = Image.open(qr_file)
    qr_width = int(label_height_px * 0.65)  # QR code size
    qr_img = qr_img.resize((qr_width, qr_width))
    qr_x = int(label_width_px - qr_width - (label_width_px * 0.05))  # Align to right side
    qr_y = int(label_height_px * 0.25)  # Adjust vertical position
    label.paste(qr_img, (qr_x, qr_y))

    # Add Bin Label Text ("Bin #:")
    font_bin_label = ImageFont.truetype("Helvetica", size=int(0.16 * label_height_px))
    bin_label_x = int(label_width_px * 0.05)  # Align to left margin
    bin_label_y = int(label_height_px * 0.15)  # Adjusted for spacing

    # Add Bin Location Value (wrapped if necessary)
    font_bin_value = ImageFont.truetype("Helvetica", size=int(0.3 * label_height_px))
    max_chars_per_line = 5  # Characters before wrapping
    wrapped_lines = [bin_location[i:i + max_chars_per_line] for i in range(0, len(bin_location), max_chars_per_line)]
    bin_value_y = bin_label_y + font_bin_label.size + 5
    line_height = font_bin_value.size + 2
    for i, line in enumerate(wrapped_lines):
        draw.text((bin_label_x, bin_value_y + i * line_height), line, fill="black", font=font_bin_value)

    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_path = temp_file.name
        label.save(temp_path, dpi=(dpi, dpi))

    # Cleanup QR temp file
    os.remove(qr_file)

    return temp_path


# label_file = create_1x3_product_label(
#     qr_data="1234567890",
#     barcode_data="9876543210",
#     description="Example ProductExample ProductExample ProductExample ProductExample Product",
#     bin_location="BinLocationBinLocationBinLocationBinLocationBinLocation",
#     product_code="9876543210",
#     title="My Label Title"
# )
# print(f"Label saved to {label_file}")


# shelf_label_file = create_2x4_shelf_label(
#     bin_location="AA10",  # Bin location text
#     title="EquipmentShare"         # Title for the label
# )
# print(f"2x4 Shelf label saved to {shelf_label_file}")




