'''module for handling multiple files, meant to be an extension of the VanGonography module\n
How it works: Initialize the VanGons class, with a cover image an list of files you want to hide.\n
`v = VanGons(["files to hide"], "cover image")`\n
`v.encode("output directory")` # to hide files into an image\n
`v.decode("encoded_cover_image", "output directory")` # to decode files from an encoded image\n
`Note:`\n
rgba images, i.e images with shape(row, colomn, 4) doesn't work currently and will result in the error,\n
`could not broadcast input array from shape (3,) into shape (4,)`'''

import os
from PIL import Image
import numpy as np
import shutil
from utils import *
import time

class VanGons:
    """class for handling multiple files, 
    meant to be an extension of the VanGonography module.\n
    Arguments to be passed when initializing.\n
    `VanGons(files: list[str], cover_image: str)`"""
    def __init__(self, files: list[str], cover_image: str) -> None:
        self.files = files
        self.image = cover_image
        self.SINGLE_RGB_BIT_SIZE = 8
        self.SINGLE_RGB_PIXEL_BIT_SIZE = self.SINGLE_RGB_BIT_SIZE * 3

    def add_headers(self, image: str, extensions: list[str], data_lengths: list[int]) -> None:
        """
        Adds header to the cover image before hiding data.\n
        For VanGons extention

        Parameters:
        - image (str): Path to the cover image.
        - extension (list): List of file extension to be hidden.
        - data_length (list): List with lengths of the data to be hidden.

        Returns:
        None
        """
        
        try:
            # Check if the image file exists
            with open(image, 'rb'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image}")

        # Check if the extension is a non-empty string
        if not extensions:
            raise ValueError("Invalid extension. It should be a non-empty list of strings.")

        # Check if data_length is a positive integer

        if not data_lengths:
            raise ValueError("Invalid data length. It should be a list of positive integer.")
        
        # check if len of extensions length and data_lengths are the same
        if len(extensions) != len(data_lengths):
            raise IndexError(f"Number of elements in extensions '{len(extensions)}'"
                             f" and data_lengths '{len(data_lengths)}' should match.")

        # Read the cover image
        try:
            with Image.open(image, "r") as cover:
                cover_array = np.array(cover)
        except Exception as e:
            raise Exception(f"Error opening the cover image: {e}")

        # Getting the height of the cover image (we will write the header vertically)
        height = cover_array.shape[0]

        
        total_bits_needed = 0 #intial value
        max_bits_available = (height - 1) * self.SINGLE_RGB_PIXEL_BIT_SIZE # Height - 1 pixels, 3 channels (RGB), 8 bits per channel
        row_count = 0 #intial value
        for extension, data_length in zip(extensions, data_lengths):
            # Convert extension and data_length to binary and get their lengths
            extension_binary = text_to_binary(extension)
            extension_length = len(extension_binary)

            data_length_binary = text_to_binary(str(data_length))
            data_length_length = len(data_length_binary)

            total_bits_needed += (extension_length + data_length_length) # increment total_bits_needed

            # Writing the extension length and data length length to the number of required horizontal pixels
            cover_array[row_count, 0] = [extension_length, data_length_length, 0]
            row_count += 1 # to move to the next row; first column
        else: # runs after the for loop; should be modified to take ext length and data length length into account
            # Check if the data to be hidden is small enough to fit in the image
            cover_array[0, 0][2] = len(data_lengths) # store number of files hidden in the B of the first pixel
            if total_bits_needed > max_bits_available:
                raise ValueError("Data to be hidden is too large for the given image.")
        
        # we initialize the starting index to hide the bits of the extension_binary and data_length_binary
        # outside the loop at to increment it in the loop to index each file binary bits properly
        starting_index_r = row_count
        starting_index_g = row_count
        pixel_bits_used = 3 # Number of bits we will use in each pixel

        for extension, data_length in zip(extensions, data_lengths):
            # Convert extension and data_length to binary
            extension_binary = text_to_binary(extension)
            extension_length = len(extension_binary)

            data_length_binary = text_to_binary(str(data_length))
            data_length_length = len(data_length_binary)

            # Writing the extension to the next pixels, we will use the 3 red channel bits of each pixel
            pixels_needed_r = np.ceil(extension_length / pixel_bits_used).astype(int) # Number of pixels needed to store the extension

            for i in range(pixels_needed_r):
                # Get the RGB values of the current pixel
                # We start at what row_count currently is because that is where the pixel we haven't used starts
                r, g, b = cover_array[i + starting_index_r, 0]
                
                # Get the bits of the extension that will be stored in the current pixel
                extension_bits = extension_binary[i * pixel_bits_used : (i + 1) * pixel_bits_used].ljust(pixel_bits_used, '0')
                # Convert the bits to an integer
                extension_int = int(extension_bits, 2)
                
                # Modify the last 3 bits of the red channel
                r = (r & 0b11111000) | extension_int # 0b11111000 is used to clear the last 3 bits of the red channel
                
                # Replace the RGB values of the current pixel with the modified RGB values
                cover_array[i + starting_index_r, 0] = [r, g, b]
            
            # Writing the data length to the next pixels, we will use the 3 green channel bits of each pixel
            # We start at what row_count currently is because that is where the pixel we haven't used starts
            pixels_needed_g = np.ceil(data_length_length / pixel_bits_used).astype(int)

            for i in range(pixels_needed_g):
                # Get the RGB values of the current pixel
                r, g, b = cover_array[i + starting_index_g, 0]
                
                # Get the bits of the data length that will be stored in the current pixel
                data_length_bits = data_length_binary[i * pixel_bits_used : (i + 1) * pixel_bits_used].ljust(pixel_bits_used, '0')

                # Convert the bits to an integer
                data_length_int = int(data_length_bits, 2)
                
                # Modify the last 3 bits of the green channel
                g = (g & 0b11111000) | data_length_int
                
                # Replace the RGB values of the current pixel with the modified RGB values
                cover_array[i + starting_index_g, 0] = [r, g, b]
            
            starting_index_r += pixels_needed_r
            starting_index_g += pixels_needed_g
            
        # save modified image        
        try:
            Image.fromarray(cover_array).save(image, format="PNG")
        except Exception as e:
            raise Exception(f"Error saving the modified cover image: {e}")
        
    def get_headers(self, image: str) -> dict[str, list]:
        '''creates a dict of the haeaders of the cover image'''
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
        else: # get no of files hidden in the image
            hfiles = int(cover_array[0,0][2])

        # list for storing list of extension_length and data_length_length for each file hidden
        ext_data_lengths = list() 

        for nfile in range(hfiles):
            try:
                *ext_data_lengths_list, _ = cover_array[nfile, 0]
            except IndexError:
                raise ValueError("Invalid image format. Header information not found.")
            else:
                ext_data_lengths.append(ext_data_lengths_list)
        
        extensions = list() # list for storing converted extension_binary to text
        data_lengths = list() # list for storing converted data_length_binary to text

        start_index_r = hfiles
        start_index_g = hfiles

        for extension_length, data_length_length in ext_data_lengths:
            # Get the extension from the next pixels, we will use the 3 red channel bits of each pixel
            extension_binary = ""
            pixel_bits_used = 3  # Number of bits we will use in each pixel
            pixels_needed_r = np.ceil(extension_length / pixel_bits_used).astype(int)

            for i in range(pixels_needed_r):
                # Get the RGB values of the current pixel
                try:# We start at start_index_r = hfiles because it is the same with no of used pixels
                    # i.e, the row we start at should be after the rows we used for storing extension_length/data_length_length
                    # for the no of hidden files(hfiles)
                    r, _, _ = cover_array[i + start_index_r, 0]  
                except IndexError:
                    raise ValueError("Invalid image format. Insufficient pixels for extension.")
                else:
                    # Get the last 3 bits of the red channel
                    extension_bits = f"{r & 0b00000111:03b}"
                    # Add the bits to the extension
                    extension_binary += extension_bits
            
            # Remove extra bits beyond the extension length
            extension_binary = extension_binary[:extension_length]

            # Convert the extension to text
            try:
                extension = binary_to_text(extension_binary)
            except ValueError as e:
                raise ValueError(f"Error converting extension to text: {e}")
            else:
                #add to extensions list
                extensions.append(extension) # add extension to list

            # Get the data length from the next pixels, we will use the 3 green channel bits of each pixel
            data_length_binary = ""
            pixels_needed_g = np.ceil(data_length_length / pixel_bits_used).astype(int)
           
            for i in range(start_index_g, start_index_g + pixels_needed_g):
                # Get the RGB values of the current pixel
                try:
                    _, g, _ = cover_array[i, 0]
                except IndexError:
                    raise ValueError("Invalid image format. Insufficient pixels for data length.")
                else:
                    # Get the last 3 bits of the green channel
                    data_length_bits = f"{g & 0b00000111:03b}"
                    # Add the bits to the data length
                    data_length_binary += data_length_bits

            # Remove extra bits beyond the data length
            data_length_binary = data_length_binary[:data_length_length]

            # Convert the data length to text and remove null characters
            try:
                data_length = binary_to_text(data_length_binary).replace('\x00', '')
            except ValueError as e:
                raise ValueError(f"Error converting data length to text: {e}")
            else:
                data_lengths.append(int(data_length))
            
            # increment pixels_needed to the appropriate start index for next file
            start_index_r += pixels_needed_r
            start_index_g += pixels_needed_g

        return {
            "extensions": extensions,
            "data_lengths": data_lengths
        }
        
    def encode_files(self, output_directory: str) -> None:
        '''for encoding multiple files to an image.\n
        output_directory: Dir to save image'''
        print('please wait, cheking files...', end='')
        time.sleep(1)
        try:
            # Check if the cover image file exists
            with open(self.image, 'rb'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Cover image file not found: {self.image}")
        
        # Read the cover image and work with it
        try:
            with Image.open(self.image, 'r') as cover:
                cover_array = np.array(cover)
        except Exception as e:
            raise Exception(f"Error opening the cover image: {e}.\nMake sure it is a valid image file.")

        # Getting the width and height of the cover image
        width = cover_array.shape[1]
        height = cover_array.shape[0]
        size_needed = width * height * (self.SINGLE_RGB_PIXEL_BIT_SIZE * 2)

        data_lengths = [] # initialize list to contain data_length
        extensions = [] # initialize list for the extension

        # Get the binary data of a file to hide to check if size fits
        for file in self.files:
            try:
                # Check if the file to hide exists
                with open(file, 'rb') as f:
                    mdata = "".join([f"{byte:08b}" for byte in f.read()])
            except FileNotFoundError:
                raise FileNotFoundError(f"File to hide not found: {file}")
            else:
                data_lengths.append(len(mdata))
                # Get the extension of the file to hide
                extension = os.path.splitext(file)[1][1:]
                extensions.append(extension) # add extension to list

        # Checking if the cover image is large enough to hide the data
        if size_needed < sum(data_lengths):
            raise ValueError("Cover image is too small to hide the data.")
    
        file_index = 0 # to track/verify which file that is being written
        r_track = -1 # tracks the row each bit is hidden for each file
        c_track = 0 # tracks the column each bit is hidden for each file

        for ind, file in enumerate(self.files):
        
            # Get the binary data of a file to hide
            with open(file, "rb") as f:
                data = "".join([f"{byte:08b}" for byte in f.read()])

            bitmask = 0b11111100  # Used to clear the last two bits of a number
            data_index = 0
    
            clear_previous_print_value()
            percents = range(100+1); ptrack = set()#to track printed percentages

            # Looping through each pixel in the cover image
            if ind == file_index: # makes sure it loops per file

                # Looping through each pixel in the cover image
                for i in range(1, width):  # Loop through each column
                    c_track += 1
                    r_track = -1 # resets row for every column loop

                    # Checking if there's still data to hide
                    if data_index >= len(data):
                        break  # Exit the outer loop if all data is processed

                    for j in range(height):  # Loop through each row
                        r_track += 1

                        # Checking if there's still data to hide
                        if data_index >= len(data):
                            break  # Exit the inner loop if all data is processed

                        # Modify the last two bits of each channel
                        for k in range(3):
                            if data_index < len(data):
                                cover_array[r_track, c_track][k] = (cover_array[r_track, c_track][k] & bitmask) | int(data[data_index:data_index + 2], 2)
                                data_index += 2  # Increment the data index by 2 because we're processing 2 bits at a time
                                # print percentages
                                percentage = int(((data_index - len(data)) / len(data)) * 100 + 100)
                                if percentage in percents and percentage not in ptrack:
                                    ptrack.add(percentage)
                                    print(f' Hiding file {ind+1}...{percentage}%', end='\r')
                            else:
                                break

                # Save the modified cover image as "Cover_{extension}.png"
                output_filename = f"Cover.png"
                if output_directory:
                    output_filename = os.path.join(output_directory, output_filename)
                
                try:
                    Image.fromarray(cover_array).save(output_filename, format="PNG")
                except Exception as e:
                    raise Exception(f"Error saving the modified cover image: {e}")
                      
            # increment to next file index checker
            file_index += 1
        else:
            clear_previous_print_value()
            print(f'Process Complete!!!\n'
                  f'Image with Hidden file(s) "{os.path.basename(output_filename)}" '
                  f'saved succefully at "{os.path.dirname(output_filename)}"')

        # Add header to the modified cover image(outside for loop)
        try:
            self.add_headers(output_filename, extensions, data_lengths)
        except Exception as e:
            raise Exception(f"Error adding header to the modified cover image: {e}")

    def decode_files(self, image: str, output_directory: str) -> None:
        '''for decoding multiple files from a cover image.\n
        image: Cover image
        output_directory: Dir to save image'''
        try:
            # Check if the image file exists
            with open(image, 'rb'):
                pass
        except FileNotFoundError:
            raise FileNotFoundError(f"Image file not found: {image}")
        else:
            print('Image with hidden file(s) is being processed...')
            time.sleep(1)

        try:
            # Get header information
            header_info = self.get_headers(image)
            extensions = [ext.replace("\x01", "_") for ext in header_info["extensions"]]
            data_lengths = header_info["data_lengths"]
        except Exception as e:
            raise Exception(f"Error decoding header information: {e}")

        try:
            with Image.open(image, 'r') as steg_image:
                steg_array = np.array(steg_image)
        except Exception as e:
            raise Exception(f"Error opening the stego image: {e}")

        width = steg_array.shape[1]
        height = steg_array.shape[0]

        unmask_bit = 0b00000011 # used to get the last two bits of a number
        
        r_track = -1 # tracks the row each bit is hidden for each file
        c_track = 0 # tracks the column each bit is hidden for each file

        for hfile in range(len(extensions)):
            data_index = 0
            binary_string = ''

            clear_previous_print_value()
            percents = range(100+1); ptrack = set()#to track printed percentages

            for i in range(1, width):  # Loop through each column, skips first(will contain header)

                c_track += 1
                r_track = -1 # resets row each coloumn

                # Checking if there's still data to hide
                if data_index >= data_lengths[hfile]:
                    break  # Exit the outer loop if all data is processed

                for j in range(height):  # Loop through each row

                    r_track += 1

                    # Checking if there's still data to hide
                    if data_index >= data_lengths[hfile]:
                        break  # Exit the outer loop if all data is processed
                    
                    for k in range(3):
                        if data_index < data_lengths[hfile]:
                            binary = f"{(steg_array[r_track, c_track][k] & unmask_bit):02b}"
                            binary_string += binary
                            data_index += 2

                            # print percentages
                            percentage = int(((data_index - data_lengths[hfile]) / data_lengths[hfile]) * 100 + 100)
                            if percentage in percents and percentage not in ptrack:
                                ptrack.add(percentage)
                                print(f' Decoding file {hfile+1}...{percentage}%', end='\r')
                        else:
                            break
            binary_string = binary_string[:data_lengths[hfile]]
            
            # Saving the file
            output_filename = f"Output-{hfile+1}.{extensions[hfile]}"
            
            if output_directory:
                output_filename = os.path.join(output_directory, output_filename)
            
            try:
                # Make a file out of the binary string then adding the file extension
                binary_to_file(binary_string, output_filename)
            except Exception as e:
                raise Exception(f"Error creating output file: {e}")
            else:
                hfile+=1
                print(f"successfully extracted file '{os.path.basename(output_filename)}' to '{os.path.dirname(output_filename)}'")
    
