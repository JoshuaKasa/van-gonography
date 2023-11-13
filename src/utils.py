import os
from PIL import Image

def get_file_size(file_path: str) -> int:
    size = os.path.getsize(file_path)
    return size * 8 # Return in bits

def binary_to_text(binary: str) -> str:
    text = "".join([chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)])
    return text

def text_to_binary(text: str) -> str:
    binary = "".join([format(ord(char), '08b') for char in text])
    return binary

def binary_to_int(binary: str) -> int:
    integer = int(binary, 2)
    return integer

def binary_to_file(binary_string, filename):
    byte_array = bytearray(int(binary_string[i:i+8], 2) for i in range(0, len(binary_string), 8))
    with open(filename, 'wb') as f:
        f.write(byte_array)

def binary_to_int(binary: str) -> int:
    integer = int(binary, 2)
    return integer

def is_image_file(filename):
    try:
        with Image.open(filename):
            return True
    except:
        return False