import os
import dearpygui.dearpygui as dpg
import transcripts_to_ebook


def change_button_txt_file_btn_data():
    dpg.configure_item("txt_file_btn", label=f"Create {dpg.get_value('file_format_menu')} file from transcript")


def load_color_button_textures():
    # Make this function more universal, lots of images to import lots of copy pasting of this part will!
    path = "resources/color_combinations"
    for colorcombo in os.listdir(path):
        width, height, channels, data = dpg.load_image("resources/color_combinations/" + colorcombo)
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag=colorcombo)



def color_buttons_popup():
    with dpg.window(label="Color themes", popup=True, show=False, id="color_buttons_popup", no_title_bar=True, pos=[300, 300]):
        height, width = 15, 150
        path = "resources/color_combinations"
        for colorcombo in os.listdir(path):
            if "outline" in colorcombo:
                pass
            else:
                dpg.add_image_button(colorcombo, user_data=colorcombo, height=height, width=width,
                                        parent="color_picker_popup", callback=set_color_combo)


def draw_color_buttons(name):
    
    height, width = 15, 150
    if name == "dir":
        path = "resources/color_combinations"
        for colorcombo in os.listdir(path):
            if "outline" in colorcombo:
                pass
            else:
                dpg.add_image_button(colorcombo, user_data=colorcombo, height=height, width=width,
                                     parent="color_picker_popup", callback=set_color_combo)
    elif name == "color_combo_name":
        dpg.add_image_button(texture_tag="combo1.png", user_data="combo1.png", tag=name, parent="color_picker_settings",
                             height=height,
                             width=width)


def set_color_combo(sender, data, data1):
    dpg.configure_item("color_combo_name", texture_tag=data1, user_data=data1)
    dpg.configure_item("color_buttons_popup", show=False)
    transcripts_to_ebook.draw_thumbnail()


def file_created_window():
    with dpg.window(label="File was created", modal=True, show=False, id="file_created_window", no_title_bar=True, min_size=[440, 70], pos=[300, 300]):
        file_format = dpg.get_value("file_format_menu")
        dpg.add_text(f"{file_format} file was created you can find it in the root folder of the program")
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="OK", pos=[180, 50], width=80, callback=lambda: dpg.configure_item("file_created_window", show=False))


def main_window():
    with dpg.font_registry():
        with dpg.font("resources/Ubuntu-R.ttf", 15) as font1:
            # FIXME: Add support for "all" the languages
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Korean)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Full)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Chinese_Simplified_Common)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Thai)
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Vietnamese)
            # Czech support - this probably adds support for lots of languages too
            dpg.add_font_chars([0x00C1,0x00E1, 0x00C9, 0x00E9, 0x011A, 0x011B , 0x00CD, 0x00ED , 0x00D3, 0x00F3 , 0x00DA, 0x00FA, 0x016E, 0x016F, 0x00DD, 0x00FD, 0x010C, 0x010D, 0x010E, 0x010F, 0x0147, 0x0148, 0x0158, 0x0159, 0x0160, 0x0161, 0x0164, 0x0165, 0x017D, 0x017E])
    load_color_button_textures()

    with dpg.window(pos=[0, 0], autosize=True, no_collapse=True, no_resize=True, no_close=True, no_move=True,
                    no_title_bar=True, tag="Primary Window"):
        dpg.bind_font(font1)
        with dpg.group(horizontal=True):
            with dpg.child_window(width=623, tag="youtube_link", border=False):
                # TODO insert input_text automagicaly from clipboard
                dpg.add_text("Youtube URL:")
                with dpg.group(horizontal=True, width=0):
                    dpg.add_input_text(tag="youtubethingy", callback=transcripts_to_ebook.do_the_youtube_thingy,
                                       on_enter=True, width=523)
                    dpg.add_button(tag="youtubethingy_buttons", label="Get transcript",
                                   callback=transcripts_to_ebook.do_the_youtube_thingy)
                dpg.add_text("List of languages:")
                dpg.add_listbox(tag="listoflanguages", callback=transcripts_to_ebook.draw_transcript, width=623)
                with dpg.group(horizontal=True):
                    with dpg.group(width=350):
                        dpg.add_text("Cover:")
                        with dpg.child_window(tag="thumbnail_drawlist", width=323, height=442, border=True):
                            dpg.add_text(label="placeholder", show=False)
                    with dpg.group(width=265):
                        dpg.add_text("Settings:")
                        with dpg.child_window(tag="settings_drawlist", width=337, height=442, border=False):
                            dpg.add_text(label="placeholder", show=False)
                            dpg.add_checkbox(tag="autogenerated_chkbx", label="Show autogenerated transcripts",
                                             callback=transcripts_to_ebook.do_the_youtube_thingy)
                            dpg.add_checkbox(tag="timestamps_chkbx", label="Add timestamps",
                                             callback=transcripts_to_ebook.do_the_youtube_thingy)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Format:")
                                dpg.add_combo(("EPUB", "TXT"), default_value="EPUB",
                                              callback=change_button_txt_file_btn_data, tag="file_format_menu",
                                              width=100)

                            with dpg.group(tag="color_picker_settings"):
                                dpg.add_text("Cover color combination:")
                                # draw_color_buttons("color_combo_name")
                                dpg.add_image_button(texture_tag="combo1.png", user_data="combo1.png", tag="color_combo_name", height=15, width=150, 
                                                    callback=lambda: dpg.configure_item("color_buttons_popup", show=True))
                            dpg.add_checkbox(label="Show outline", tag="outline_chkbx",
                                             callback=transcripts_to_ebook.draw_thumbnail)

                dpg.add_spacer()
                with dpg.group(horizontal=True, width=0):
                    dpg.add_button(tag="txt_file_btn",
                                   label=f"Create {dpg.get_value('file_format_menu')} file from the transcript",
                                   callback=transcripts_to_ebook.create_a_file, height=50, width=623)

            with dpg.child_window(tag="Transcript", width=445):
                dpg.add_text("Transcript: ")


def load_gui():
    dpg.create_context()
    main_window()
    file_created_window()
    color_buttons_popup()

    dpg.create_viewport(title="Create ebook from Youtube video transcript", width=1092, height=687, resizable=False)

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    load_gui()
