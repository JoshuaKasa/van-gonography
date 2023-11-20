#### <p align="center">Hide any type of files inside a image of your choice</p>

![Terminal image](img/Terminal.png)

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/JoshuaKasa/van-gonography/commits/master">
    <img src="https://img.shields.io/github/last-commit/JoshuaKasa/van-gonography.svg" alt="GitHub last commit">
  </a>
  <a href="https://www.buymeacoffee.com/yourbestfriendjoshua">
    <img src="https://img.shields.io/badge/Buy%20Me%20a-Beer-yellow.svg" alt="Buy Me a Beer">
  </a>
</p>


# Table of Contents

- [Introduction](#introduction)
- [How it works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

# Introduction

I've recently had this amazing idea of how could it would be to hide an entire file inside an image, I thought I would've been the first in history to come up with this idea, but of course... I wasn't. <br>
I did some research and found out that this technique is called [steganography](https://en.wikipedia.org/wiki/Steganography) and it's been around for a while now. The general idea behing it is built all around the fact that images, are composed by bits and every bit is composed by 3 channels that make up the color for that pixel, which are called RGB (Red, Green, Blue). Each channel is composed by 8 bits, which means that each channel can have 256 different values, which means that each pixel can have 256^3 different colors, WHICH MEANS... that each pixel can have 16,777,216 different colors. <br>
That's A LOT of colors, and that's why we can hide data inside images, because we can change the color of a pixel by just a little bit and the human eye won't even be able to notice the difference. You know another cool thing? Text files are all made up of bits, therefore, we can substitute the 2 last bits of the color channels of each pixel with the bits of a text file and the image will still look the same, but the text file will be hidden inside the image. 

# How it works

Right now, you might be wondering how an entire file can stay inside an image without changing its appearance. Well, it's actually pretty simple.

If you don't know, every file inside your computer, from .exe to .jpg, is stored using bits, which are literally just 1s and 0s. For example, the letter `A` is stored as `01000001`, and the letter `B` is stored as `01000010`. This means that your 1 gigabyte porn video is actually just stored as a bunch of 1s and 0s! To be exact:

$$\ \text{Size} = 1 \, \text{GB} \times 1024 \, \text{MB/GB} \times 1024 \, \text{KB/MB} \times 1024 \, \text{bytes/KB} \times 8 \, \text{bits/byte} \$$

$$\ \text{Size} = 8,589,934,592 \, \text{bits} \$$

Now, another very important thing to know is that images are made up of pixels, and each pixel gets its color from a format called RGB (Red, Green, Blue). Each of those letters corresponds to a channel, numbered from 0 to 255 (1 byte), meaning each channel can have 256 different values.

These numbers can also be represented in binary, with each channel composed of 8 bits. Let's say we have a pixel with the color `(0xFF, 0x00, 0x00)`, which is red (because we are modifying the first channel, which is R, red). This means that the pixel is composed of the following bits: `11111111 00000000 00000000`. As files are also composed of bits, we can take the first 2 bits of a file and substitute them with the first 2 bits of a channel, resulting in: `11111111 00000000 00000011`. Repeat this process for every pixel in the image, and for every bit in the file, to hide the file inside the image without changing its appearance.

And there you have it! That's how you hide a file inside an image. Now, if you want to know how to do it in Python, you can check out the code in this repository, it's pretty simple and easy to understand.

We can also see this as a simple matrix operation:
\documentclass{article}
\usepackage{amsmath}

\begin{document}

We can also see this as a simple matrix operation:

Let $I$ be a matrix representing an image, where each element $p_{ij}$ corresponds to a pixel value represented as a hexadecimal number $pv$. This hexadecimal number is decomposed into three channels $R$ (red), $G$ (green), and $B$ (blue), each consisting of values in the range $[0, 255)$.

Consider a file $F$, where each bit is denoted by $b$. Let $\{p_{i,j}^{(l)}\}$ represent a series of pixels in the image, where $i$ is the x-coordinate, $j$ is the y-coordinate, and $l$ is the length of the series.

Define the operation $\mathcal{B}$ that extracts 2 bits from each $p_{ij}^{(l)}$ and replaces these 2 bits with the corresponding bits from the last channel ($c_b$) of the pixel. This process is iteratively applied until all bits from the file $F$ are embedded into the image.

This can be expressed as follows:

$$
\begin{align*}
\mathcal{B}: \{p_{ij}^{(l)}\} &\rightarrow \{p_{ij}^{(l)}\}, \text{ where} \\
p_{ij}^{(l)} &= (p_{ij}^{(l)R}, p_{ij}^{(l)G}, p_{ij}^{(l)B}) \\
\mathcal{B}(x) &= x \bmod 4 \\
\text{For } k &= 1, 2, \ldots, n, \text{ the operation is given by} \\
&\quad b_k \rightarrow \mathcal{B}(p_{ij}^{(l)B_k}) = \sum_{k=1}^{n} \mathcal{B}(p_{ij}^{(l)B_k})
\end{align*}

\end{document}
$$

# Installation

```bash
# Clone the repository
git clone https://github.com/JoshuaKasa/van-gonography.git

# Change the working directory to van-gonography
cd van-gonography

# Install the required dependencies
pip install -r requirements.txt
```

# Usage

For running the program in the UI mode (simpler and easier to use but also less useful for developers) just run the following command:

```bash
python vangonography.py
```

For running the program in the CLI mode (more complicated but with a bit more functionalities) just run the following command:
```bash
python vangonography.py -cli
```
You can then use the following arguments along with it:
```console
usage: vangonography.py [-h] [-ood] [-l LOG_FILE] [-cli] [-o OUTPUT_DIR] [-v] [-s] [-e] [-d] [-c COVER_IMAGE]
                        [-f HIDDEN_FILE]

Van Gonography is a steganography tool that hides files in images.

options:
  -h, --help            show this help message and exit

Optional arguments:
  -ood                  Open file after decoding from image (default: False)
  -l LOG_FILE, --log LOG_FILE
                        Log file for the program (default: False)
  -cli                  Run the program in CLI mode, this means there's not gonna be any menu (default: False)
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        Output directory for the modified image or revealed file
  -v, --version         Show the version number and exit

Positional arguments (only used in CLI mode):
  -s, --show            Show the difference between two images (default: False)
  -e, --encode          Encode the file in the image (default: False)
  -d, --decode          Decode the file hidden in the image (default: False)
  -c COVER_IMAGE, --cover COVER_IMAGE
                        Image to be used for hiding or revealing, positional only when using decoding, encoding or
                        differentiate
  -f HIDDEN_FILE, --file HIDDEN_FILE
                        File to be hidden
```
For example, if you want to hide a file called `secret.txt` inside an image called `image.png` and you want to save the modified image in a folder called `output` you would run the following command:
```bash
python vangonography.py -cli -e -c [Absolute path to your `image.png` cover image] -f [Absolute path to your `secret.txt` file] -o Output
```
This will create a directory called `Output` in the same directory as the program and inside it will be a file called `Cover_txt.png` which will be the modified image with the hidden file inside it. If you want to decode the file from the image you would run the following command:
```bash
python vangonography.py -cli -d -c [Absolute path (or not) to your `Cover_txt.png` cover image] -o Output
```
If you also want to create a log.log file with all the information about the program you can run the following command:
```bash
python vangonography.py -cli -d -c [Absolute path (or not) to your `Cover_txt.png` cover image] -o Output -l
```

# License

MIT © Van Gonography
[MIT](LICENSE)

# Contributing

Pull requests are more than welcome, I love seeing people contribute to my projects and I'll make sure to look at every single one of them. Feel free to contribute translations, features, bug fixes or anything else you think it's necessary, even documentation and README files!
**if you get any errors, please open an issue and I'll try to fix it as soon as possible :<wbr>)**