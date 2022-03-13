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

def draw_color_buttons(name):
    height, width = 15, 150
    if name == "dir":
        path = "resources/color_combinations"
        for colorcombo in os.listdir(path):
            if "outline" in colorcombo:
                pass
            else:
                dpg.add_image_button(colorcombo, user_data=["color_combo_name", colorcombo], height=height, width=width,
                                     parent="color_picker_popup", callback=set_color_combo)
    elif name == "color_combo_name":
        dpg.add_image_button(texture_tag="combo1.png", tag=name, parent="color_picker_settings", height=height,
                             width=width)


def set_color_combo(sender, data, data1):
    dpg.configure_item(data1[0], texture_tag=data1[1], user_data=data1[1])


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

    load_color_button_textures()

    with dpg.window(pos=[0, 0], autosize=True, no_collapse=True, no_resize=True, no_close=True, no_move=True,
                    no_title_bar=True, tag="Primary Window"):
        dpg.bind_font(font1)
        with dpg.group(horizontal=True):
            with dpg.child_window(width=645, tag="youtube_link", border=False):
                # TODO insert input_text automagicaly from clipboard
                dpg.add_text("Youtube URL:")
                with dpg.group(horizontal=True, width=0):
                    dpg.add_input_text(tag="youtubethingy", callback=transcripts_to_ebook.do_the_youtube_thingy, on_enter=True, width=523)
                    dpg.add_button(tag="youtubethingy_buttons", label="Get transcript", callback=transcripts_to_ebook.do_the_youtube_thingy)
                dpg.add_text("List of languages:")
                dpg.add_listbox(tag="listoflanguages", callback=transcripts_to_ebook.draw_transcript, width=623)
                with dpg.group(horizontal=True):
                    with dpg.group(width=335):
                        dpg.add_text("Cover:")
                        with dpg.child_window(tag="thumbnail_drawlist", width=330, height=198, border=True):
                            dpg.add_text(label="placeholder", show=False)
                    with dpg.group(horizontal=True, width=265):
                        with dpg.child_window(tag="settings_drawlist", height=198, width=100, border=False):
                            dpg.add_text("Settings")
                            dpg.add_checkbox(tag="autogenerated_chkbx", label="Show autogenerated transcripts",
                                             callback=transcripts_to_ebook.do_the_youtube_thingy)
                            dpg.add_checkbox(tag="timestamps_chkbx", label="Add timestamps",
                                             callback=transcripts_to_ebook.do_the_youtube_thingy)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Format:")
                                dpg.add_combo(("EPUB", "TXT"), default_value="TXT",
                                              callback=change_button_txt_file_btn_data, tag="file_format_menu",
                                              width=100)
                            with dpg.group(tag="color_picker_settings"):
                                dpg.add_text("Cover color combination:")
                                draw_color_buttons("color_combo_name")
                                with dpg.popup("color_combo_name", mousebutton=dpg.mvMouseButton_Left,
                                               tag="color_picker_popup"):
                                    dpg.add_text("Choose color combination")
                                    dpg.add_separator()
                                    draw_color_buttons("dir")
                                dpg.add_button(tag="create_cover", label="Show cover", callback=transcripts_to_ebook.show_cover)

                with dpg.group(horizontal=True, width=0):
                    dpg.add_button(tag="txt_file_btn",
                                   label=f"Create {dpg.get_value('file_format_menu')} file from the transcript",
                                   callback=transcripts_to_ebook.create_a_file, height=50, width=623)

            with dpg.child_window(tag="Transcript", width=445):
                dpg.add_text("Transcript: ")

def load_gui():
    dpg.create_context()
    main_window()
    dpg.create_viewport(title="Create ebook from Youtube video transcript", width=1113, height=442, resizable=False)

    
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    load_gui()
