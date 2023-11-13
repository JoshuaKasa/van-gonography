import os
import io

import numpy as np

from PIL import Image
from tkinter import Tk, filedialog

SINGLE_RGB_BIT_SIZE = 8 # Each RGB value is composed of 3 colors, each color is composed of 8 bits
SINGLE_RGB_PIXEL_BIT_SIZE = SINGLE_RGB_BIT_SIZE * 3 # Each pixel is composed of 3 RGB values, each RGB value is composed of 3 colors, each color is composed of 8 bits

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

# Function for adding a header to the image
from PIL import Image
import numpy as np
import io

def add_header(image: str, extension: str, data_length: int) -> None:
    """
    Adds a header to the cover image before hiding data.

    Parameters:
    - image (str): Path to the cover image.
    - extension (str): File extension to be hidden.
    - data_length (int): Length of the data to be hidden.

    Returns:
    None
    """
    # Read the cover image
    with Image.open(image, "r") as cover:
        cover_array = np.array(cover)

        # Getting the height of the cover image (we will write the header vertically)
        height = cover_array.shape[0]

        # Convert extension and data_length to binary and get their lengths
        extension_binary = text_to_binary(extension)
        extension_length = len(extension_binary)
        
        data_length_binary = text_to_binary(str(data_length))
        data_length_length = len(data_length_binary)
        
        # Writing the extension length and data length length to the first pixel
        cover_array[0, 0] = [extension_length, data_length_length, 0]
        
        # Writing the extension to the next pixels, we will use the 3 red channel bits of each pixel
        pixel_bits_used = 3 # Number of bits we will use in each pixel
        pixels_needed = np.ceil(extension_length / pixel_bits_used).astype(int) # Number of pixels needed to store the extension
        
        for i in range(pixels_needed):
            # Get the RGB values of the current pixel
            r, g, b = cover_array[i + 1, 0] # We start at 1 because we already used the first pixel
            
            # Get the bits of the extension that will be stored in the current pixel
            extension_bits = extension_binary[i * pixel_bits_used : (i + 1) * pixel_bits_used].ljust(pixel_bits_used, '0')
            
            # Convert the bits to an integer
            extension_int = int(extension_bits, 2)
            
            # Modify the last 3 bits of the red channel
            r = (r & 0b11111000) | extension_int # 0b11111000 is used to clear the last 3 bits of the red channel
            
            # Replace the RGB values of the current pixel with the modified RGB values
            cover_array[i + 1, 0] = [r, g, b]
            
        # Writing the data length to the next pixels, we will use the 3 green channel bits of each pixel
        starting_index = 1 + pixels_needed # We start at 1 because we already used the first pixel
        pixels_needed = np.ceil(data_length_length / pixel_bits_used).astype(int)
        
        for i in range(starting_index, starting_index + pixels_needed):
            # Get the RGB values of the current pixel
            r, g, b = cover_array[i, 0]
            
            # Get the bits of the data length that will be stored in the current pixel
            data_length_bits = data_length_binary[(i - starting_index) * pixel_bits_used : (i - starting_index + 1) * pixel_bits_used].ljust(pixel_bits_used, '0')

            
            # Convert the bits to an integer
            data_length_int = int(data_length_bits, 2)
            
            # Modify the last 3 bits of the green channel
            g = (g & 0b11111000) | data_length_int
            
            # Replace the RGB values of the current pixel with the modified RGB values
            cover_array[i, 0] = [r, g, b]
            
        # Save the modified cover image
        output_filename = "Cover.png"
        with io.BytesIO() as output:  # Using BytesIO to save the image in memory
            Image.fromarray(cover_array).save(output, format="PNG")  # Convert the numpy array to an image and save it to the BytesIO object
            output.seek(0)  # Move the cursor to the beginning of the BytesIO object
            with open(output_filename, "wb") as f:
                f.write(output.read())  # Write the contents of the BytesIO object to a file
              
def get_header(image: str) -> dict:
    with Image.open(image, "r") as cover:
        cover_array = np.array(cover)

        # Get the extension length and data length length from the first pixel
        extension_length, data_length_length, _ = cover_array[0, 0]

        # Get the extension from the next pixels, we will use the 3 red channel bits of each pixel
        extension = ""
        pixel_bits_used = 3  # Number of bits we will use in each pixel
        pixels_needed = np.ceil(extension_length / pixel_bits_used).astype(int)

        for i in range(pixels_needed):
            # Get the RGB values of the current pixel
            r, _, _ = cover_array[i + 1, 0]  # We start at 1 because we already used the first pixel

            # Get the last 3 bits of the red channel
            extension_bits = f"{r & 0b00000111:03b}"

            # Add the bits to the extension
            extension += extension_bits

        # Remove extra bits beyond the extension length
        extension = extension[:extension_length]

        # Convert the extension to text
        extension = binary_to_text(extension)

        # Get the data length from the next pixels, we will use the 3 green channel bits of each pixel
        starting_index = 1 + pixels_needed  # We start at 1 because we already used the first pixel
        pixels_needed = np.ceil(data_length_length / pixel_bits_used).astype(int)

        data_length = ""

        for i in range(starting_index, starting_index + pixels_needed):
            # Get the RGB values of the current pixel
            _, g, _ = cover_array[i, 0]

            # Get the last 3 bits of the green channel
            data_length_bits = f"{g & 0b00000111:03b}"

            # Add the bits to the data length
            data_length += data_length_bits

        # Remove extra bits beyond the data length
        data_length = data_length[:data_length_length]

        # Convert the data length to text and remove null characters
        data_length = binary_to_text(data_length).replace('\x00', '')

        return {
            "extension": extension,
            "data_length": int(data_length)
        }

# Getting the RGB of each pixel in the cover image, then converting it to binary and modifying the LSB
def encode_image(file: str, image: str) -> None:
    
    # Get the binary data of a file to hide
    with open(file, "rb") as f:
        data = "".join([f"{byte:08b}" for byte in f.read()])
    data_length = len(data)
    
    # Get the extension of the file to hide
    extension = os.path.splitext(file)[1][1:]
    
    # Read the cover image and work with it
    with Image.open(image, 'r') as cover:
        cover_array = np.array(cover)
        
        # Getting the width and height of the cover image
        width = cover_array.shape[1]
        height = cover_array.shape[0]
        
        # Checking if the cover image is large enough to hide the data
        if width * height * SINGLE_RGB_PIXEL_BIT_SIZE * 2 < data_length:
            raise Exception("Cover image is too small to hide the data.")
        
        data_index = 0
        bitmask = 0b11111100 # Used to clear the last two bits of a number
        
        # Looping through each pixel in the cover image
        for i in range(1, width): # Loop through each column
            for j in range(height): # Loop through each row
                
                # Checking if there's still data to hide
                if data_index >= len(data):
                    break  # Exit the inner loop if all data is processed

                # Get the RGB values of the current pixel
                r, g, b = cover_array[j, i]
                
                # Modify the last two bits of each channel
                for k in range(3):
                    if data_index < len(data):
                        cover_array[j, i][k] = (cover_array[j, i][k] & bitmask) | int(data[data_index:data_index + 2], 2)
                        data_index += 2 # Increment the data index by 2 because we're processing 2 bits at a time
                    else:
                        break
                
        # Save the modified cover image as "Cover.png"
        Image.fromarray(cover_array).save("Cover.png", format="PNG")
        
        add_header("Cover.png", extension, data_length)
                            
def decode_image(image):
    extension = get_header(image)["extension"].replace("\x01", "_")
    data_length = get_header(image)["data_length"]
    
    with Image.open(image, 'r') as steg_image:
        steg_array = np.array(steg_image)
        
        width = steg_array.shape[1]
        height = steg_array.shape[0]
        
        # This is a bit hard to explain but basically, we're getting the last two bits of each RGB value and concatenating them to form a binary string
        binary_string = "".join([
            f"{(steg_array[j, i][0] & 0b00000011):02b}{(steg_array[j, i][1] & 0b00000011):02b}{(steg_array[j, i][2] & 0b00000011):02b}"
            for i in range(1, width) for j in range(height) if data_length > 0
        ])
        binary_string = binary_string[:data_length] # Truncate the binary string to the length of the data
    
    # Make a file out of the binary string then adding the file extension
    binary_to_file(binary_string, f"Output.{extension}")

def differentiate_image(source, cover):
    # Get the 2 images as numpy arrays
    with Image.open(source, 'r') as source_image, Image.open(cover, 'r') as cover_image:
        source_array = np.array(source_image)
        cover_array = np.array(cover_image)
        
        # We only get 1 image's width and height because we assume that the 2 images have the same dimensions
        width = source_array.shape[1]
        height = source_array.shape[0]
        
        # Create a new image called "Difference.png" that will show the scaled difference between the source and cover images
        difference_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Loop through each pixel in the source and cover images
        for i in range(width):
            for j in range(height):
                # Get the RGB values of the current pixel at both images
                r, g, b = source_array[j, i]
                r2, g2, b2 = cover_array[j, i]
                
                # Scale the differences to a visible range (e.g., 0-255)
                scaled_difference = (
                    # Adding 128 to the difference to make it visible
                    np.uint8(min(255, max(0, np.int16(r2) - np.int16(r) + 128))), 
                    np.uint8(min(255, max(0, np.int16(g2) - np.int16(g) + 128))),
                    np.uint8(min(255, max(0, np.int16(b2) - np.int16(b) + 128)))
                )
                
                difference_array[j, i] = scaled_difference
        
        # Go look code for encode_image() to understand how this works
        with io.BytesIO() as output:
            Image.fromarray(difference_array).save(output, format="PNG")
            output.seek(0)
            with open("Difference.png", "wb") as f:
                f.write(output.read())
                
if __name__ == "__main__":
    # Remember the image with the hidden is always called "Cover.png"
    
    # Get the file to hide
    root = Tk()
    root.withdraw()
    file = filedialog.askopenfilename(title="Select file to hide")
    
    # Get the cover image
    root = Tk()
    root.withdraw()
    image = filedialog.askopenfilename(title="Select cover image")
    
    # Hide the file in the cover image
    encode_image(file, image)
    
    # Differentiate the source and cover images
    differentiate_image(file, "Cover.png")