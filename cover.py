# Importing the Pillow library
from PIL import Image, ImageDraw, ImageFont
import os
from urllib.request import urlretrieve


def text_wrapper(text, font, max_width):
    # Totally not stolen from eyong kevin https://gist.github.com/Eyongkevin/adbac2334f1355d8045111c264d80621
    list_of_lines = []
    if font.getlength(text) <= max_width:
        return text
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than the image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getlength(line + words[i]) <= max_width:
                line = line + words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            list_of_lines.append(f"{line}")
        new_line = "\n"
        return new_line.join(list_of_lines)


def create_cover(url, video_thumbnail_path, author, title):
    # Cover size = 1280 x 1650
    path = "tmp/thumbnail_author_cover.jpg"
    if os.path.exists(path):
        os.remove(path)
        urlretrieve(url, path)
    else:
        urlretrieve(url, path)

    myfont = ImageFont.truetype("resources/Ubuntu-R.ttf", 80)

    image_cover = Image.new("RGB", (1280, 1650), "white")
    image_top = Image.new("RGB", (1280, 465), "white")
    image_icon = Image.open(path)
    image_top_draw = ImageDraw.Draw(image_top)
    image_top_draw.text((100, 320), text_wrapper(author, myfont, 1000), font=myfont, fill=(0, 0, 0))
    image_thumbnail = Image.open(video_thumbnail_path)
    image_bottom = Image.new("RGB", (1280, 465), "white")
    image_bottom_draw = ImageDraw.Draw(image_bottom)

    # FIXME: Implement text resizing based on height of the text.
    image_bottom_draw.multiline_text((100, 100), text_wrapper(title, myfont, 1180), font=myfont, fill=(0, 0, 0))

    image_cover.paste(image_top, (0, 0))
    image_cover.paste(image_icon, (100, 100))
    image_cover.paste(image_thumbnail, (0, 465))
    image_cover.paste(image_bottom, (0, 720+465))
    image_cover.show()
    path = "tmp/cover.jpg"
    image_cover.save(path)
    return path


def main():
    url = "https://yt3.ggpht.com/ytc/AKedOLR8EP18dz9h1mInmZPQSYdjv-RN-te55pbRKfubEA=s176-c-k-c0x00ffffff-no-rj"
    video_thumbnail_path = "tmp/thumbnailmaxres.jpg"
    author = "Learn Italian with Lucrezia"
    title = "Learn 18 useful Italian adjectives to describe personality in Italian (Sub)"
    create_cover(url, video_thumbnail_path, author, title)


if __name__ == "__main__":
    main()


