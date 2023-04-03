from PIL import Image
import requests
import os
from io import BytesIO

# ASCII_CHARS_BRIGHT = list(reversed([*"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1\{\}[]?-_+~<>i!lI;:,\"^`'. "]))
ASCII_CHARS_BRIGHT = [*" .:-=+*#%@"] # for bright pictures
ASCII_CHARS_DARK = list(reversed(ASCII_CHARS_BRIGHT)) # for dark pictures

def get_image(imageUrl, scale_factor=0.75, width=os.get_terminal_size().columns):
    image = ""
    try:
        imageUrl = imageUrl
        image = ascii_convertor(imageUrl, scale_factor, width)
    except:
        image = ""
    return image

def resize(image, new_width = 100, tuner = 0.5):
    width, height = image.size
    aspect_ratio = height / width 
    new_height = new_width * aspect_ratio * tuner
    return image.resize((new_width, int(new_height)))

def to_greyscale(image):
    return image.convert("L") # grayscale

def convert(image):
    pixels = image.getdata()
    dark_threshold = 100
    darkCount = 0
    for pixel in pixels:
        if pixel < dark_threshold:
            darkCount += 1
    palette = ASCII_CHARS_BRIGHT if (darkCount / float(len(pixels))) <= 0.5 else ASCII_CHARS_DARK
    # print(palette)
    ascii_str = ""
    for pixel in pixels:
        newIntensityIdx = min(pixel // 25, len(palette) - 1)
        ascii_str += palette[newIntensityIdx] # put entire image into one string
    return ascii_str


def ascii_convertor(imageUrl, scale_factor=0.5, width=os.get_terminal_size().columns):
    response = requests.get(imageUrl)
    image = Image.open(BytesIO(response.content))
    image = resize(image, int(width * scale_factor))
    greyscaleImage = to_greyscale(image)
    ascii_str = convert(greyscaleImage)
    ascii_img=""
    for i in range(0, len(ascii_str), greyscaleImage.width):
        ascii_img += ascii_str[i:i+greyscaleImage.width] + "\n" # place each "row" into the image
    return ascii_img

def main():
    # path = input("Enter the path to the image field: \n")
    # try:
    #     image = PIL.Image.open(path)
    # except:
    #     print(path, "Unable to find image ")
    path = "drake.jfif"
    image = Image.open(path)
    #resize image
    image = resize(image)
    #convert image to greyscale image
    greyscale_image = to_greyscale(image)
    # convert greyscale image to ascii characters
    ascii_str = convert(greyscale_image)
    img_width = greyscale_image.width
    ascii_str_len = len(ascii_str)
    ascii_img=""
    #Split the string based on width  of the image
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i+img_width] + "\n"
    #save the string to a file
    with open("ascii_image.txt", "w") as f:
        f.write(ascii_img)
    print(ascii_img)
# main()
