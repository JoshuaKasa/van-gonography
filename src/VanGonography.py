import os
import io
import sys
import zlib
import json
import logging
import argparse

import numpy as np

from PIL import Image
from colorama import Fore, init
from tkinter import Tk, filedialog
from __version__ import __version__
from cryptography.fernet import Fernet

from utils import *

SINGLE_RGB_BIT_SIZE = 8 # Each RGB value is composed of 3 colors, each color is composed of 8 bits
SINGLE_RGB_PIXEL_BIT_SIZE = SINGLE_RGB_BIT_SIZE * 3 # Each pixel is composed of 3 RGB values, each RGB value is composed of 3 colors, each color is composed of 8 bits

def add_header(image: str, extension: str, data_length: int, output_directory: str = "") -> None:
    """
    Adds a header to the cover image before hiding data.

    Parameters:
    - image (str): Path to the cover image.
    - extension (str): File extension to be hidden.
    - data_length (int): Length of the data to be hidden.

    Returns:
    None
    """
    try:
        # Check if the image file exists
        with open(image, 'rb') as img_file:
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image}")

    # Check if the extension is a non-empty string
    if not extension or not isinstance(extension, str):
        raise ValueError("Invalid extension. It should be a non-empty string.")

    # Check if data_length is a positive integer
    if not isinstance(data_length, int) or data_length <= 0:
        raise ValueError("Invalid data length. It should be a positive integer.")

    # Read the cover image
    try:
        with Image.open(image, "r") as cover:
            cover_array = np.array(cover)
    except Exception as e:
        raise Exception(f"Error opening the cover image: {e}")

    # Getting the height of the cover image (we will write the header vertically)
    height = cover_array.shape[0]

    # Convert extension and data_length to binary and get their lengths
    extension_binary = text_to_binary(extension)
    extension_length = len(extension_binary)
    
    data_length_binary = text_to_binary(str(data_length))
    data_length_length = len(data_length_binary)

    # Check if the data to be hidden is small enough to fit in the image
    total_bits_needed = extension_length + data_length_length
    max_bits_available = (height - 1) * 3 * 8  # Height - 1 pixels, 3 channels (RGB), 8 bits per channel
    if total_bits_needed > max_bits_available:
        raise ValueError("Data to be hidden is too large for the given image.")

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
        
    try:
        Image.fromarray(cover_array).save(image, format="PNG")
    except Exception as e:
        raise Exception(f"Error saving the modified cover image: {e}")

              
def get_header(image: str) -> dict:
    
    try:
        # Check if the image file exists
        with open(image, 'rb'):
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image}")

    try:
        with Image.open(image, "r") as cover:
            cover_array = np.array(cover)
    except Exception as e:
        raise Exception(f"Error opening the cover image: {e}")

    # Get the extension length and data length length from the first pixel
    try:
        extension_length, data_length_length, _ = cover_array[0, 0]
    except IndexError:
        raise ValueError("Invalid image format. Header information not found.")

    # Get the extension from the next pixels, we will use the 3 red channel bits of each pixel
    extension = ""
    pixel_bits_used = 3  # Number of bits we will use in each pixel
    pixels_needed = np.ceil(extension_length / pixel_bits_used).astype(int)

    for i in range(pixels_needed):
        # Get the RGB values of the current pixel
        try:
            r, _, _ = cover_array[i + 1, 0]  # We start at 1 because we already used the first pixel
        except IndexError:
            raise ValueError("Invalid image format. Insufficient pixels for extension.")

        # Get the last 3 bits of the red channel
        extension_bits = f"{r & 0b00000111:03b}"

        # Add the bits to the extension
        extension += extension_bits

    # Remove extra bits beyond the extension length
    extension = extension[:extension_length]

    # Convert the extension to text
    try:
        extension = binary_to_text(extension)
    except ValueError as e:
        raise ValueError(f"Error converting extension to text: {e}")

    # Get the data length from the next pixels, we will use the 3 green channel bits of each pixel
    starting_index = 1 + pixels_needed  # We start at 1 because we already used the first pixel
    pixels_needed = np.ceil(data_length_length / pixel_bits_used).astype(int)

    data_length = ""

    for i in range(starting_index, starting_index + pixels_needed):
        # Get the RGB values of the current pixel
        try:
            _, g, _ = cover_array[i, 0]
        except IndexError:
            raise ValueError("Invalid image format. Insufficient pixels for data length.")

        # Get the last 3 bits of the green channel
        data_length_bits = f"{g & 0b00000111:03b}"

        # Add the bits to the data length
        data_length += data_length_bits

    # Remove extra bits beyond the data length
    data_length = data_length[:data_length_length]

    # Convert the data length to text and remove null characters
    try:
        data_length = binary_to_text(data_length).replace('\x00', '')
    except ValueError as e:
        raise ValueError(f"Error converting data length to text: {e}")

    return {
        "extension": extension,
        "data_length": int(data_length)
    }

# Getting the RGB of each pixel in the cover image, then converting it to binary and modifying the LSB
def encode_image(file: str, image: str, output_directory: str = "", encrypt: bool = False, compress = False) -> None:
    try:
        # Check if the file to hide exists
        with open(file, 'rb') as f:
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"File to hide not found: {file}")

    try:
        # Check if the cover image file exists
        with open(image, 'rb') as img_file:
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Cover image file not found: {image}")

    # Get the binary data of a file to hide
    with open(file, "rb") as f:
        data = "".join([f"{byte:08b}" for byte in f.read()])
    data_length = len(data)
   
    # Compress the data if the user wants to
    if compress:
        try:
            data = zlib.compress(data.encode())
        except Exception as e:
            raise Exception(f"Error compressing the data: {e}")
        data_length = len(data) # Update the data length
    data = "".join([f"{byte:08b}" for byte in data]) # Convert the data back to binary (zlib compresses the data and converts it to bytes)

    # If the user wants to encrypt the data (python vangonography.py -cli -e --encrypt -f tests/input/Test.txt -o C:\Users\jizos\Desktop -c ..\img\Cat.jpg)
    if encrypt:
        key = Fernet.generate_key() # Generate a key for encryption
        with open("key.key", "wb") as key_file:
            key_file.write(f"This is your encryption key, keep it safe, you will need it to decrypt the data: {key}".encode()) # Write the key to a file
        # Encrypt the data
        try:
            f = Fernet(key) # Create a Fernet object
            data = f.encrypt(data.encode()) # Encrypt the data
            data = "".join([f"{byte:08b}" for byte in data]) # Convert the data back to binary (Fernet encrypts the data and converts it to bytes)
        except Exception as e:
            raise Exception(f"Error encrypting the data: {e}")

    # Get the extension of the file to hide
    extension = os.path.splitext(file)[1][1:]

    # Read the cover image and work with it
    try:
        with Image.open(image, 'r') as cover:
            cover_array = np.array(cover)
    except Exception as e:
        raise Exception(f"Error opening the cover image: {e}")

    # Getting the width and height of the cover image
    width = cover_array.shape[1]
    height = cover_array.shape[0]

    # Checking if the cover image is large enough to hide the data
    if width * height * SINGLE_RGB_PIXEL_BIT_SIZE * 2 < data_length:
        raise ValueError("Cover image is too small to hide the data.")

    data_index = 0
    bitmask = 0b11111100  # Used to clear the last two bits of a number

    # Looping through each pixel in the cover image
    for i in range(1, width):  # Loop through each column
        for j in range(height):  # Loop through each row

            # Checking if there's still data to hide
            if data_index >= len(data):
                break  # Exit the inner loop if all data is processed

            # Get the RGB values of the current pixel
            r, g, b = cover_array[j, i]

            # Modify the last two bits of each channel
            for k in range(3):
                if data_index < len(data):
                    cover_array[j, i][k] = (cover_array[j, i][k] & bitmask) | int(data[data_index:data_index + 2], 2)
                    data_index += 2  # Increment the data index by 2 because we're processing 2 bits at a time
                else:
                    break
                
    # Save the modified cover image as "Cover_{extension}.png"
    output_filename = f"Cover_{extension}.png"
    if encrypt:
        output_filename = f"Cover_{extension}_encrypted.png"
    if output_directory:
        output_filename = os.path.join(output_directory, output_filename)
    
    try:
        Image.fromarray(cover_array).save(output_filename, format="PNG")
    except Exception as e:
        raise Exception(f"Error saving the modified cover image: {e}")

    # Add header to the modified cover image
    try:
        add_header(output_filename, extension, data_length, output_filename)
    except Exception as e:
        raise Exception(f"Error adding header to the modified cover image: {e}")
                            
def decode_image(image, output_directory: str = "", open_on_success: bool = False, decrypt: bool = False, key: str = "", compressed = False) -> None:
    try:
        # Check if the image file exists
        with open(image, 'rb'):
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image}")

    try:
        # Get header information
        header_info = get_header(image)
        extension = header_info["extension"].replace("\x01", "_")
        data_length = header_info["data_length"]
    except Exception as e:
        raise Exception(f"Error decoding header information: {e}")

    try:
        with Image.open(image, 'r') as steg_image:
            steg_array = np.array(steg_image)
    except Exception as e:
        raise Exception(f"Error opening the stego image: {e}")

    width = steg_array.shape[1]
    height = steg_array.shape[0]

    # This is a bit hard to explain, but basically, we're getting the last two bits of each RGB value and concatenating them to form a binary string
    binary_string = "".join([
        f"{(steg_array[j, i][0] & 0b00000011):02b}{(steg_array[j, i][1] & 0b00000011):02b}{(steg_array[j, i][2] & 0b00000011):02b}"
        for i in range(1, width) for j in range(height) if data_length > 0
    ])
    binary_string = binary_string[:data_length]  # Truncate the binary string to the length of the data
    
    # If the initial data was compressed, decompress it (TODO: Add a way to check if the data was compressed without needing the user to specify it)
    if compressed:
        try:
            binary_string = zlib.decompress(binary_string.encode())
        except Exception as e:
            raise Exception(f"Error decompressing the data: {e}")
        binary_string = "".join([f"{byte:08b}" for byte in binary_string]) # Convert the data back to binary (zlib compresses the data and converts it to bytes)

    # If the user wants to decrypt the data
    if decrypt:
        if not key:
            # Additional error checking
            raise ValueError("No key was given, you must give a key to decrypt the data.") # Check if the user gave a key
        try:
            f = Fernet(key) # Create a Fernet object
            binary_string = f.decrypt(binary_string.encode()) # Decrypt the data
        except Exception as e:
            raise Exception(f"Error decrypting the data: {e}")

    # Saving the file
    output_filename = f"Output.{extension}"
    if output_directory:
        output_filename = os.path.join(output_directory, output_filename)
    
    try:
        # Make a file out of the binary string then adding the file extension
        binary_to_file(binary_string, output_filename)
    except Exception as e:
        raise Exception(f"Error creating output file: {e}")
    
    # Open the file if the user wants to
    if open_on_success:
        try:
            os.startfile(output_filename)
        except Exception as e:
            raise Exception(f"Error opening output file make sure you have the right program to open it: {e}")

def differentiate_image(source, cover, output_directory: str = "") -> None:
    try:
        # Check if the source image file exists
        with open(source, 'rb'):
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Source image file not found: {source}")

    try:
        # Check if the cover image file exists
        with open(cover, 'rb'):
            pass
    except FileNotFoundError:
        raise FileNotFoundError(f"Cover image file not found: {cover}")

    try:
        # Get the source and cover images as numpy arrays
        with Image.open(source, 'r') as source_image, Image.open(cover, 'r') as cover_image:
            source_array = np.array(source_image)
            cover_array = np.array(cover_image)
    except Exception as e:
        raise Exception(f"Error opening source or cover image: {e}")

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

    # Go look at the code for encode_image() to understand how this works
    output_filename = "Difference.png"
    if output_directory:
        output_filename = os.path.join(output_directory, output_filename)
    
    try:
        Image.fromarray(difference_array).save(output_filename, format="PNG")
    except Exception as e:
        raise Exception(f"Error saving the difference image: {e}")
                
def main():
    
    os.system('cls' if os.name == 'nt' else 'clear') # Clear the terminal
    
    # Argument parser
    parser = argparse.ArgumentParser(description="Van Gonography is a steganography tool that hides files in images.")
    
    # Optional arguments
    optional_group = parser.add_argument_group('Optional arguments')
    optional_group.add_argument("-ood", dest="ood", action="store_true", default=False, help="Open file after decoding from image (default: False)")
    optional_group.add_argument("-l", "--log", dest="log", action="store_true", default=False, help="Log file for the program (default: False)")
    optional_group.add_argument("-cli", dest="cli", action="store_true", default=False, help="Run the program in CLI mode, this means there's not gonna be any menu (default: False)")
    optional_group.add_argument("-o", "--output", dest="output", type=str, metavar="OUTPUT_DIR", help="Output directory for the modified image or revealed file")
    optional_group.add_argument("-v", "--version", action="version", version=f"VanGonography v{__version__}", help="Show the version number and exit")
    optional_group.add_argument("--encrypt", dest="encrypt", action="store_true", default=False, help="Encrypt the data before hiding it (default: False)")
    optional_group.add_argument("--decrypt", dest="decrypt", action="store_true", default=False, help="Decrypt the data after revealing it (default: False)")
    optional_group.add_argument("--key", dest="key", type=str, metavar="KEY", help="Key to decrypt the data (default: None)")
    optional_group.add_argument("--json", dest="json", type=str, metavar="JSON_FILE", help="JSON file containing the arguments (default: None)")
    optional_group.add_argument("--stealth", dest="stealth", action="store_true", default=False, help="Hides the file in stealth mode (default: False)") # TODO: Implement this shit
    # For anyone wondering, I have no idea how to implement the stealth mode, so if you want to share some ideas
    optional_group.add_argument("-z", "--zip", dest="zip", action="store_true", default=False, help="Zip or unzips the file (default: False")
    
    
    # Positional arguments group (only used in CLI mode)
    positional_group = parser.add_argument_group('Positional arguments (only used in CLI mode)')
    positional_group.add_argument("-s", "--show", dest="show", action="store_true", default=False, help="Show the difference between two images (default: False)")
    positional_group.add_argument("-e", "--encode", dest="encode", action="store_true", default=False, help="Encode the file in the image (default: False)")
    positional_group.add_argument("-d", "--decode", dest="decode", action="store_true", default=False, help="Decode the file hidden in the image (default: False)")
    positional_group.add_argument("-c", "--cover", dest="cover", type=str, metavar="COVER_IMAGE", help="Image to be used for hiding or revealing, positional only when using decoding, encoding or differentiate")
    positional_group.add_argument("-f", "--file", dest="file", type=str, metavar="HIDDEN_FILE", help="File to be hidden")

    args = parser.parse_args()
    
    # Getting the json file and setting the arguments
    if args.json:
        with open(args.json, "r") as json_file:
            json_data = json.load(json_file)
            json_data.pop("desc") # Removing the description argument for not causing errors when setting the attributes
            
        for key, value in json_data.items(): # Looping through the json file data
            if hasattr(args, key): # Checking if the key exists in the args variable
                setattr(args, key, value) # The args variable is a Namespace object
            else:
                print(f"Invalid argument was passed, double check the argument name and try again: {key}")
                logging.error(f"Invalid argument: {key}")
                return
    
    # Checking for CLI mode
    if args.cli:
        # Logging setup 
        if args.log:
            # If the user wants to log, we will create the log.log file
            if args.log == True:
                args.log = "log.log"
            
            logging.basicConfig(
                filename=args.log,
                level=logging.DEBUG,
                format="%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            
            logging.info("Logging started")
            logging.info(f"Arguments: {args}")
        
        # CLI mode starts here
        if args.cover: # Checking if a cover image is given (essential for both decoding and encoding)
            
            # Full error checking for encryption and decryption
            if args.encrypt and args.decrypt:
                print("You can't encrypt and decrypt at the same time, choose one.")
                logging.error("You can't encrypt and decrypt at the same time, choose one.")
                return
            elif args.decrypt and not args.key:
                print("You must give a key to decrypt the data.")
                logging.error("No key was given, you must give a key to decrypt the data.")
                return
            
            # Is the user choosing to encode or decode?
            if args.encode: # Encode
                # Checking if a file to hide is given
                if not args.file:
                    print("You must insert the file to hide")
                    logging.error("No file to hide was given")
                    return
                try:
                    logging.info("Encoding started") # Logging the start
                    logging.info(f"Encoding {args.file} in {args.cover}") # Logging the file and cover image
                    
                    encode_image(args.file, args.cover, args.output, args.encrypt, args.zip) # Encoding the file
                    
                    print(f"File hidden successfully in {args.cover}.") 
                    logging.info(f"File hidden successfully in {args.cover}.") # Logging the success message, this is also useful for checking the time it took to hide the file
                except Exception as e:
                    print(f"An error occurred: {e}")
                    logging.error(f"An error occurred: {e}")
                    
            # Checking for decode
            elif args.decode:
                if args.file:
                    print("You can't insert the file you must only insert the image with the hidden file and optionally the output directory.")
                    logging.error("A file to hide was given, but you must only insert the image with the hidden file and optionally the output directory.")
                    
                try:
                    logging.info("Decoding started") # Logging the start
                    logging.info(f"Decoding {args.cover}") # Logging the cover image
                    
                    decode_image(args.cover, args.output, args.ood, args.decrypt, args.key, args.zip) # Decoding the file
                    
                    print(f"File revealed successfully from {args.cover}.")
                    logging.info(f"File revealed successfully from {args.cover}.") # Same as above
                except Exception as e:
                    print(f"An error occurred: {e}")
                    logging.error(f"An error occurred: {e}")
                    
            # Checking for differentiating images
            elif args.show:
                if args.file:
                    print("You can't insert the file to hide you must only insert the source and cover images and optionally the output directory.")
                    logging.error("A file to hide was given, but you must only insert the source and cover images and optionally the output directory.")
                try:
                    logging.info("Differentiating started") # Logging the start
                    logging.info(f"Differentiating {args.cover} and {args.file}") # Logging the source and cover images
                    
                    differentiate_image(args.cover, args.output)
                    
                    print(f"Difference image saved successfully as Difference.png.")
                    logging.info(f"Difference image saved successfully as Difference.png.") # Again, same as above
                except Exception as e:
                    print(f"An error occurred: {e}")
                    logging.error(f"An error occurred: {e}")
                    
            # Something's wrong
            else:
                print("Invalid arguments.")
                logging.error("Invalid arguments, you must choose a mode to run the program in between encode, decode and show.")
        else:
            print("You must insert all the required arguments, no cover image was given, use -h for help.")
            logging.error("No cover image was given, for checking all the arguments use -h in CLI mode.")
    
    # Using UI mode if no arguments are given
    else:
        
        # Checking if any arguments are given
        if args.show or args.encode or args.decode or args.output or args.cover or args.file:
            print("You can't use arguments in UI mode.")
            return
        
        # UI mode
        init(autoreset=True)
        print(
            """
                                               ,----..                                                                              ,---,                           ,---,       ,----..       ,----..    
       ,---.                                  /   /   \                                                                 ,-.----.  ,--.' |                        ,`--.' |      /   /   \     /   /   \   
      /__./|                   ,---,         |   :     :    ,---.        ,---,    ,---.               __  ,-.           \    /  \ |  |  :                       /    /  :     /   .     :   /   .     :  
 ,---.;  ; |               ,-+-. /  |        .   |  ;. /   '   ,'\   ,-+-. /  |  '   ,'\   ,----._,.,' ,'/ /|           |   :    |:  :  :                      :    |.' '    .   /   ;.  \ .   /   ;.  \ 
/___/ \  | |   ,--.--.    ,--.'|'   |        .   ; /--`   /   /   | ,--.'|'   | /   /   | /   /  ' /'  | |' | ,--.--.   |   | .\ ::  |  |,--.     .--,         `----':  |   .   ;   /  ` ;.   ;   /  ` ; 
\   ;  \ ' |  /       \  |   |  ,"' |        ;   | ;  __ .   ; ,. :|   |  ,"' |.   ; ,. :|   :     ||  |   ,'/       \  .   : |: ||  :  '   |   /_ ./|            '   ' ;   ;   |  ; \ ; |;   |  ; \ ; | 
 \   \  \: | .--.  .-. | |   | /  | |        |   : |.' .''   | |: :|   | /  | |'   | |: :|   | .\  .'  :  / .--.  .-. | |   |  \ :|  |   /' :, ' , ' :            |   | |   |   :  | ; | '|   :  | ; | ' 
  ;   \  ' .  \__\/: . . |   | |  | |        .   | '_.' :'   | .; :|   | |  | |'   | .; :.   ; ';  ||  | '   \__\/: . . |   : .  |'  :  | | /___/ \: |            '   : ;   .   |  ' ' ' :.   |  ' ' ' : 
   \   \   '  ," .--.; | |   | |  |/         '   ; : \  ||   :    ||   | |  |/ |   :    |'   .   . |;  : |   ," .--.; | :     |`-'|  |  ' | :.  \  ' |            |   | '   '   ;  \; /  |'   ;  \; /  | 
    \   `  ; /  /  ,.  | |   | |--'          '   | '/  .' \   \  / |   | |--'   \   \  /  `---`-'| ||  , ;  /  /  ,.  | :   : :   |  :  :_:,' \  ;   :            '   : | ___\   \  ',  /__\   \  ',  /  
     :   \ |;  :   .'   \|   |/              |   :    /    `----'  |   |/        `----'   .'__/\_: | ---'  ;  :   .'   \|   | :   |  | ,'      \  \  ;            ;   |.'/  .\;   :    /  .\;   :    /   
      '---" |  ,     .-./'---'                \   \ .'             '---'                  |   :    :       |  ,     .-./`---'.|   `--''         :  \  \           '---'  \  ; |\   \ .'\  ; |\   \ .'    
             `--`---'                          `---`                                       \   \  /         `--`---'      `---`                  \  ' ;                   `--"  `---`   `--"  `---`      
                                                                                            `--`-'                                                `--`                                                   
            """
        )
        print()
        print(Fore.YELLOW + "Version 1.0.0")
        print("Welcome to VanGonography! Please select an option:")
        print()
        print(Fore.LIGHTRED_EX + "[1] " + Fore.WHITE + "Hide a file in an image")
        print(Fore.LIGHTRED_EX + "[2] " + Fore.WHITE + "Reveal a hidden file in an image")
        print(Fore.LIGHTRED_EX + "[3] " + Fore.WHITE + "Show the difference between two images")
        print(Fore.LIGHTRED_EX + "[4] " + Fore.WHITE + "Exit")
        print()
        
        while True:
            choice = input("Enter your choice: ")
            
            if choice == "1":
                try:
                    # Get the file to hide
                    root = Tk()
                    root.withdraw()
                    file = filedialog.askopenfilename(title="Select file to hide")

                    # Check if the user canceled the file selection
                    if not file:
                        print("File selection canceled.")

                    # Get the cover image
                    root = Tk()
                    root.withdraw()
                    image = filedialog.askopenfilename(title="Select cover image")

                    # Check if the user canceled the image selection
                    if not image:
                        print("Image selection canceled.")

                    # Check if the selected file is an image
                    if not is_image_file(image):
                        print("Selected cover image is not a valid image file.")

                    # Get the output directory
                    root = Tk()
                    root.withdraw()
                    output_directory = filedialog.askdirectory(title="Select output directory")
                    
                    # Check if the user canceled the output directory selection
                    if not output_directory:
                        print("Output directory selection canceled.")
                    
                    # Check if the selected output directory is valid
                    if not os.path.isdir(output_directory):
                        print("Selected output directory is not a valid directory.")
                    
                    # Hide the file in the cover image
                    encode_image(file, image, output_directory)

                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            elif choice == "2":
                try:
                    # Get the image with the hidden file
                    root = Tk()
                    root.withdraw()
                    image = filedialog.askopenfilename(title="Select image with hidden file")

                    # Check if the user canceled the image selection
                    if not image:
                        print("Image selection canceled.")

                    # Check if the selected file is an image
                    if not is_image_file(image):
                        print("Selected image is not a valid image file.")

                    # Get the output directory
                    root = Tk()
                    root.withdraw()
                    output_directory = filedialog.askdirectory(title="Select output directory")
                    
                    # Check if the user canceled the output directory selection
                    if not output_directory:
                        print("Output directory selection canceled.")
                    
                    # Check if the selected output directory is valid
                    if not os.path.isdir(output_directory):
                        print("Selected output directory is not a valid directory.")
                    
                    # Reveal the hidden file
                    decode_image(image, output_directory)

                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            elif choice == "3":
                try:
                    # Get the source image
                    root = Tk()
                    root.withdraw()
                    source = filedialog.askopenfilename(title="Select source image")

                    # Check if the user canceled the image selection
                    if not source:
                        print("Source image selection canceled.")

                    # Check if the selected file is an image
                    if not is_image_file(source):
                        print("Selected source image is not a valid image file.")

                    # Get the cover image
                    root = Tk()
                    root.withdraw()
                    cover = filedialog.askopenfilename(title="Select cover image")

                    # Check if the user canceled the image selection
                    if not cover:
                        print("Cover image selection canceled.")

                    # Check if the selected file is an image
                    if not is_image_file(cover):
                        print("Selected cover image is not a valid image file.")

                    # Get the output directory
                    root = Tk()
                    root.withdraw()
                    output_directory = filedialog.askdirectory(title="Select output directory")
                    
                    # Check if the user canceled the output directory selection
                    if not output_directory:
                        print("Output directory selection canceled.")
                    
                    # Check if the selected output directory is valid
                    if not os.path.isdir(output_directory):
                        print("Selected output directory is not a valid directory.")
                    
                    # Show the difference between the source and cover images
                    differentiate_image(source, cover, output_directory)

                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            elif choice == "4":
                print("Exiting...")
                return
            
            else:
                print("Invalid choice.")
            
if __name__ == '__main__':
    main()
