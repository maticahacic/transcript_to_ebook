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

def get_colors_from_colorcombo_image(colorcombo_path):
    colorcombo_image = Image.open(colorcombo_path)
    colorcombo_image.convert("RGBA")
    get_pixel_color = colorcombo_image.load()
    color_top = get_pixel_color[100, 20]
    color_top_font = get_pixel_color[500, 20]
    color_bottom = get_pixel_color[1000, 20]
    color_bottom_font = get_pixel_color[1500, 20]

    return color_top, color_top_font, color_bottom, color_bottom_font


def create_cover(url, video_thumbnail_path, author, title, colorcombo, sender):
    # Cover size = 1280 x 1650
    path = "tmp/thumbnail_author_cover.jpg"
    colorcombo_path = f"resources/color_combinations/{colorcombo}"
    color_top, color_top_font, color_bottom, color_bottom_font = ["white", "black", "white", "black"]
    if os.path.exists(path):
        os.remove(path)
        urlretrieve(url, path)
    else:
        urlretrieve(url, path)
    color_top, color_top_font, color_bottom, color_bottom_font = get_colors_from_colorcombo_image(colorcombo_path)

    myfont = ImageFont.truetype("resources/Ubuntu-R.ttf", 50)
    print(color_top_font)
    image_cover = Image.new("RGBA", (1280, 1650), "white")
    image_top = Image.new("RGBA", (1280, 465), color=color_top)
    image_icon = Image.open(path)
    image_icon.convert("RGBA")
    image_top_draw = ImageDraw.Draw(image_top)
    image_top_draw.text((100, 320), text_wrapper(author, myfont, 1000), font=myfont, fill=color_top_font)
    image_thumbnail = Image.open(video_thumbnail_path)
    image_thumbnail.convert("RGBA")
    image_bottom = Image.new("RGBA", (1280, 465), color =color_bottom)
    image_bottom_draw = ImageDraw.Draw(image_bottom)

    # FIXME: Implement text resizing based on height of the text.
    image_bottom_draw.multiline_text((100, 100), text_wrapper(title, myfont, 1180), font=myfont, fill=color_bottom_font)

    image_cover.paste(image_top, (0, 0))
    image_cover.paste(image_icon, (100, 100))
    image_cover.paste(image_thumbnail, (0, 465))
    image_cover.paste(image_bottom, (0, 720+465))
    layer1 = image_cover.convert("RGBA")
    layer_rectangle = Image.new("RGBA", layer1.size, color=(0, 0, 0, 0))
    outline_rectangle = (color_top_font[0], color_top_font[1], color_top_font[2], 100)
    ImageDraw.Draw(layer_rectangle).rectangle((50, 50, 1230, 1600), outline=outline_rectangle, width=13)

    final2 = Image.alpha_composite(layer1, layer_rectangle)
    final2.show()
    if sender == "epub":
        path = "tmp/cover.png"
        final2.save(path, "PNG")
        return path
    else:
        # TODO: Add creation of thumbnail and "drawing" it into gui
        pass


def main():
    url = "https://yt3.ggpht.com/ytc/AKedOLR8EP18dz9h1mInmZPQSYdjv-RN-te55pbRKfubEA=s176-c-k-c0x00ffffff-no-rj"
    video_thumbnail_path = "tmp/thumbnailmaxres.jpg"
    author = "Learn Italian with Lucrezia"
    title = "Learn 18 useful Italian adjectives to describe personality in Italian (Sub)"
    create_cover(url, video_thumbnail_path, author, title, "combo2.png", "epub")


if __name__ == "__main__":
    main()


