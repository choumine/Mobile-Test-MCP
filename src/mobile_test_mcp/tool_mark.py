from .common import app
from PIL import Image, ImageDraw
from typing import Tuple

@app.tool()
async def tool_mark(image_path: str, x: int, y: int) -> str:
    """
    Draw a point with a white inner circle and black outer circle of radius 20 pixels at the specified coordinates on the image
    
    Parameters:
        image_path (str): Image file path
        x (int): X coordinate
        y (int): Y coordinate
    
    Returns:
        str: File path of the marked image
    """
    # Open image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Define radius
    radius = 20
    
    # Calculate outer circle bounding box coordinates
    outer_bbox = (x - radius, y - radius, x + radius, y + radius)
    
    # Draw outer circle (black)
    draw.ellipse(outer_bbox, fill='black')
    
    # Calculate inner circle bounding box coordinates
    inner_radius = radius // 2  # Inner circle radius is half of the outer circle, i.e. 10 pixels
    inner_bbox = (x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius)
    
    # Draw inner circle (white)
    draw.ellipse(inner_bbox, fill='white')
    
    # Generate new filename
    name, ext = image_path.rsplit('.', 1)
    marked_image_path = f"{name}_marked.{ext}"
    
    # Save marked image
    image.save(marked_image_path)
    
    return marked_image_path