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
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

# Introduction

I've recently had this amazing idea of how could it would be to hide an entire file inside an image, I thought I would've been the first in history to come up with this idea, but of course... I wasn't. I did some research and found out that this technique is called [steganography](https://en.wikipedia.org/wiki/Steganography) and it's been around for a while now. The general idea behing it is built all around the fact that images, are composed by bits and every bit is composed by 3 channels that make up the color for that pixel, which are called RGB (Red, Green, Blue). Each channel is composed by 8 bits, which means that each channel can have 256 different values, which means that each pixel can have 256^3 different colors, WHICH MEANS... that each pixel can have 16,777,216 different colors. That's A LOT of colors, and that's why we can hide data inside images, because we can change the color of a pixel by just a little bit and the human eye won't even be able to notice the difference. You know another cool thing? Text files are all made up of bits, therefore, we can substitute the 2 last bits of the color channels of each pixel with the bits of a text file and the image will still look the same, but the text file will be hidden inside the image. 

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

```bash
# Run the script
python vangonography.py

# Follow the instructions, everything is written in the title of the file selection window
```

# License

MIT © Van Gonography
[MIT](LICENSE)

# Contributing

Pull requests are more than welcome, I love seeing people contribute to my projects and I'll make sure to look at every single one of them. Feel free to contribute translations, features, bug fixes or anything else you think it's necessary, even documentation and README files!
**if you get any errors, please open an issue and I'll try to fix it as soon as possible :<wbr>)**