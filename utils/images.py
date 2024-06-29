from PIL import Image


def load_tga(image_path):
    """
    Load image in TGA format
    """
    image = Image.open(image_path)
    return image
