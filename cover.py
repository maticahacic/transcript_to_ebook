# Importing the Pillow library
from PIL import Image, ImageDraw, ImageFont
import os


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


def get_colors_from_colorcombo_image(colorcombo_path, colorcombo_outline_path):
    colorcombo_image = Image.open(colorcombo_path)
    colorcombo_outline = Image.open(colorcombo_outline_path)
    colorcombo_image.convert("RGBA")
    get_pixel_color = colorcombo_image.load()

    color_top = get_pixel_color[100, 20]
    color_top_font = get_pixel_color[500, 20]
    color_bottom = get_pixel_color[1000, 20]
    color_bottom_font = get_pixel_color[1500, 20]

    get_pixel_color = colorcombo_outline.load()
    color_outline = get_pixel_color[10, 10]
    color_outline = (color_outline[0], color_outline[1], color_outline[2], 190)

    return color_top, color_top_font, color_bottom, color_bottom_font, color_outline


def create_cover(thumbnail_author_path, video_thumbnail_path, author, title, colorcombo, sender, color_number, outline):
    # Cover size = 1280 x 1650
    colorcombo_path = f"resources/color_combinations/{colorcombo}"
    colorcombo_outline_path = f"resources/color_combinations/{colorcombo[:6]}_outline.png"

    colors_list = get_colors_from_colorcombo_image(colorcombo_path, colorcombo_outline_path)

    myfont = ImageFont.truetype("resources/Ubuntu-R.ttf", 50)
    image_cover = Image.new("RGBA", (1280, 1650), "white")
    image_top = Image.new("RGBA", (1280, 465), color=colors_list[0])
    image_icon = Image.open(thumbnail_author_path).convert("RGBA")
    image_thumbnail = Image.open(video_thumbnail_path).convert("RGBA")
    image_bottom = Image.new("RGBA", (1280, 465), color=colors_list[2])

    image_top_draw = ImageDraw.Draw(image_top)
    image_bottom_draw = ImageDraw.Draw(image_bottom)

    # FIXME: Implement text resizing based on height of the text.
    image_top_draw.text((100, 320), text_wrapper(author, myfont, 1000), font=myfont, fill=colors_list[1])
    image_bottom_draw.multiline_text((100, 100), text_wrapper(title, myfont, 1130), font=myfont, fill=colors_list[4])

    image_cover.paste(image_top, (0, 0))
    image_cover.paste(image_icon, (100, 100))
    image_cover.paste(image_thumbnail, (0, 465))
    image_cover.paste(image_bottom, (0, 720 + 465))
    


    # FIXME, add this outside. When implementing cover editor
    proper_senders = ["epub", "showcover", "thumbnail"]
    if sender in proper_senders:
        outline_rectangle = (colors_list[4][0], colors_list[4][1], colors_list[4][2], 190)
    else:
        if color_number < 4:
            outline_rectangle = (colors_list[color_number][0], colors_list[color_number][1], colors_list[color_number][2], 190)
        else:
            outline_rectangle = (colors_list[4][0], colors_list[4][1], colors_list[4][2], 190)
    
    if outline:
        layer_rectangle = Image.new("RGBA", image_cover.size, color=(0, 0, 0, 0))
        ImageDraw.Draw(layer_rectangle).rectangle((50, 50, 1230, 1600), outline=outline_rectangle, width=13)
        final_cover = Image.alpha_composite(image_cover, layer_rectangle)
    else:
        final_cover = image_cover

    # FIXME: Change from arbitray number "ifs" to more readeable form

    if sender == "epub":
        path = f"tmp/cover.png"
        final_cover.save(path, "PNG")
    elif sender == "thumbnail":
        final_cover.thumbnail((330,425))
        path = f"tmp/cover_thumbnail.png"
        final_cover.save(path, "PNG")
        return path
    else:
        # this should be used by cover.py for testing purposes only
        if color_number < 4:
            path = f"tmp/cover{colorcombo[:6]}{color_number}.png"
            final_cover.save(path, "PNG")
        elif color_number == 10:
            path = f"tmp/cover{colorcombo[:6]}{color_number}.png"
            final_cover.save(path, "PNG")
        elif color_number == 42:
            final_cover.thumbnail((256,330))
            path = f"tmp/{colorcombo[:6]}_thumbnail.png"
            final_cover.save(path, "PNG")
        elif color_number == 5:
            # This is for testing purposes only
            print("imhere")
            path = f"tmp/cover_thumbnail.png"
            final_cover.save(path, "PNG")
        return path


def generate_all(type_of_ouput):
    # Testing different color combinations and outlines of said combinations 
    author_thumbnail_path = "resources/test_graphics/author_thumbnail_test.png"
    video_thumbnail_path = "resources/test_graphics/thumbnail_test.png"
    author = "This is a test of Author Name"
    title = "This is just a Title Test Case with some words when you fill out the Youtube URL field you will see " \
                "different result"
    path = "resources/color_combinations"
    color_combinations = [0, 1, 2, 3]
    for colorcombo in os.listdir(path):
        if "outline" in colorcombo:
                    pass
        else:
            if type_of_ouput == "thumbnails":
                    create_cover(author_thumbnail_path, video_thumbnail_path, author, title, colorcombo, "epub", 42, True)
                        
            elif type_of_ouput == "all":
                    for color in color_combinations:
                            create_cover(author_thumbnail_path, video_thumbnail_path, author, title, colorcombo, "epub", color, True)

            elif type_of_ouput== "outline":
                    create_cover(author_thumbnail_path, video_thumbnail_path, author, title, colorcombo, "epub", 5, True)


def main():

    # create_cover(url, video_thumbnail_path, author, title, "combo4.png", "epub", 10)
    # generate_all_cover_options(url, video_thumbnail_path, author, title, "outline")
    # type of options 
    # "thumbnails" - generates thumbnail versions of covers
    # "outline" - generates covers from all theme files using coresponding *_outline.png file
    # "all" - generates covers using all base colors of a cover theme to get covers. Outuput is number_of_colors*number_of_combination.png_files of cover files
    generate_all("all")


if __name__ == "__main__":
    main()
