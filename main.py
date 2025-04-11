from PIL import Image, ImageDraw, ImageFont
import random
import textwrap
import requests
import base64
import io
from urllib.parse import parse_qs

def handler(event, context):
    params = parse_qs(event.get("queryStringParameters") or "")
    notbook = params.get("notbook", [""])[0]

    # Notebook layout
    lines_count = 17
    line_spacing = 70
    top_margin = 100
    bottom_margin = 100
    page_height = top_margin + (lines_count * line_spacing) + bottom_margin
    width = 800

    # Create image
    image = Image.new('RGB', (width, page_height), color=(250, 247, 240))
    draw = ImageDraw.Draw(image)

    # Red margin line
    draw.line((100, 0, 100, page_height), fill=(255, 80, 80), width=2)

    # Blue lines
    for i in range(lines_count):
        y = top_margin + i * line_spacing
        draw.line((50, y, width - 50, y), fill=(180, 200, 255), width=1)

    # Load font
    font_path = "handwriting.ttf"  # Make sure this file is in the same folder
    font_size = 59
    font = ImageFont.truetype(font_path, font_size)

    # Draw text
    x = 120
    y = top_margin
    max_chars_per_line = 43
    ink_color = (30, 30, 110)

    wrapped_lines = textwrap.wrap(notbook, width=max_chars_per_line)
    for line in wrapped_lines[:lines_count]:
        jitter_x = random.randint(-1, 1)
        jitter_y = random.randint(-1, 1)
        draw.text((x + jitter_x, y + jitter_y), line, font=font, fill=ink_color)
        y += line_spacing

    # Convert image to base64
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Upload to ImgBB
    api_key = "bbba3dcc09c031412bc35c3840ac80e3"
    upload_url = "https://api.imgbb.com/1/upload"

    response = requests.post(upload_url, data={
        "key": api_key,
        "image": img_base64
    })

    if response.status_code == 200:
        image_url = response.json()['data']['url']
        return {
            "statusCode": 200,
            "body": f'{{"url": "{image_url}"}}',
            "headers": {"Content-Type": "application/json"}
        }
    else:
        return {
            "statusCode": 500,
            "body": f'{{"error": "{response.text}"}}',
            "headers": {"Content-Type": "application/json"}
        }
