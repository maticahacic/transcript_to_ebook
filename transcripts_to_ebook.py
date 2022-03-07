import os

import requests
import dearpygui.dearpygui as dpg

from urllib.request import urlretrieve, urlopen
from urllib.parse import urlparse, parse_qs
from contextlib import suppress

from ebooklib import epub

from youtube_transcript_api import YouTubeTranscriptApi

from bs4 import BeautifulSoup as bs
import regex

dpg.create_context()


def get_video_details(type_of_detail):
    page = urlopen(dpg.get_value("youtubethingy"))
    soup = bs(page, features="html.parser")
    if type_of_detail == "title":
        # Even though there is a <title> tag in youtube page next siblings content gets
        # cleaner result
        return soup.title.next_sibling["content"]
    elif type_of_detail == "description":
        # There are <meta> tags with description inside but all of them a shortened
        # <script> tag has long description available
        description_soup = soup.findAll('script')
        regex_pattern = regex.compile(r'(?<="shortDescription":")(?s)(.*)","isCrawlable"')
        description = regex_pattern.findall(str(description_soup))[0]
        return description
    elif type_of_detail == "author":
        return soup.find("link", itemprop="name").get("content")


with dpg.font_registry():
    with dpg.font("resources/Ubuntu-R.ttf", 15) as font1:
        # FIXME: Add support for "all" the languages
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)


def create_a_file():
    # Placeholder (or so it seems) for creating files:
    # At least calls API less time till Class will be implemented
    video_id = get_video_id(dpg.get_value("youtubethingy"))
    if video_id is None:
        pass
    else:
        if dpg.get_value("file_format_menu") == "EPUB":
            create_epub_file(video_id)
        elif dpg.get_value("file_format_menu") == "TXT":
            create_text_file(video_id,
                             False)  # for now this will sta2y at manual change, till settings window is implemented
        else:
            # Room for PDF creation
            pass


def create_text_file(video_id, include_description):
    author = get_video_details('author')
    title = get_video_details('title')
    description = get_video_details('description')
    language = dpg.get_value("listoflanguages")
    paragraph = draw_transcript("create_file", None)  # If true it will return the paragraph else it will just draw them
    file = open(f"subs_as_txt_{language}.txt", "w")
    file.write(f"{title} - {author}\n")
    file.write("============================================================================\n")
    if include_description:
        file.write(f"{description}\n")
        file.write("============================================================================\n")
    else:
        pass
    file.write(paragraph)
    file.close()


def create_epub_file(video_id):
    # FIXME: Add metadata to the book from video descriptione
    author = get_video_details('author')
    title = get_video_details('title')
    description = get_video_details('description')
    language = dpg.get_value("listoflanguages")
    cover_quality = "hq"
    book = epub.EpubBook()
    book.set_identifier(video_id)
    book.set_title(title)
    book.set_language(language)
    book.add_author(author)
    get_thumbnail_youtube(video_id, cover_quality)
    book.set_cover(video_id + ".jpg", open(f"tmp/{video_id}{cover_quality}.jpg", "rb").read())

    # Description
    description = description.replace(r"\n", "<p>")
    description_chapter = epub.EpubHtml(title="Description", file_name="description.xhtml", lang=language)
    description_chapter.content = f"<html><head></head><body><h1>Video description</h1>" \
                                  f"<p>{description}</p></body></html> "

    # Transcript
    transcript_chapter = epub.EpubHtml(title='Transcript', file_name='transcript.xhtml')

    # HTMLIFY the transcript
    paragraph = draw_transcript("create_file", "html")

    transcript_chapter.content = f"<h1>Transcript</h1><p>{paragraph}</p>" \
                                 f"<p><img src='tmp/{video_id}{cover_quality}.jpg' alt='Cover Image'/></p>"

    # add chapters to the book
    book.add_item(description_chapter)
    book.add_item(transcript_chapter)
    book.toc = (description_chapter, transcript_chapter)

    # add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # define css style
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif;
    }
    h2 {
        text-align: left;
        text-transform: uppercase;
        font-weight: 200;     
    }
    ol {
            list-style-type: none;
    }
    ol > li:first-child {
            margin-top: 0.3em;
    }
    nav[epub|type~='toc'] > ol > li > ol  {
        list-style-type:square;
    }
    nav[epub|type~='toc'] > ol > li > ol > li {
            margin-top: 0.3em;
    }
    '''

    # add css file
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)

    # create spin, add cover page as first page
    book.spine = ['cover', 'nav', description_chapter, transcript_chapter]

    # create epub file
    epub.write_epub(f'{title}_{language}.epub', book, {})


def get_thumbnail_youtube(video_id, quality):
    # FIXME: This probably goes into separate class to regex etc. only once per video objectorino
    path = f"tmp/{video_id}{quality}.jpg"
    url = f"https://img.youtube.com/vi/{video_id}/{quality}default.jpg"
    if os.path.exists(path):
        pass
    else:
        urlretrieve(url, path)
    return path


def import_img_to_texture_registry(video_id):
    # FIXME: This probably goes into separate class to regex etc. only once per video objectorino
    # imports images to texture registry
    if video_id not in dpg.get_aliases():
        width, height, channels, data = dpg.load_image(f"tmp/{video_id}mq.jpg")
        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag=video_id)
        thumbnail_ratio = width / height
        drawlist_height = 180
        drawlist_width = drawlist_height * thumbnail_ratio
        dpg.add_image(video_id, height=drawlist_height, width=drawlist_width, parent="thumbnail_drawlist")
    else:
        pass


def validate_youtube_video_id_url(video_id):
    # Yes
    if video_id is None:
        return False
    else:
        request = requests.get(f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg")
        if request.status_code == 404:
            return False
        else:
            return True


def get_video_id(url, ignore_playlist=False):
    # Examples:
    # - http://youtu.be/SA2iWivDJiE
    # - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    # - http://www.youtube.com/embed/SA2iWivDJiE
    # - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    query = urlparse(url)

    if query.hostname == 'youtu.be': return query.path[1:]
    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
            # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch': return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/': return query.path.split('/')[1]
        if query.path[:7] == '/embed/': return query.path.split('/')[2]
        if query.path[:3] == '/v/': return query.path.split('/')[2]
        # returns None for invalid YouTube url


def get_list_of_available_languages(video_id, data):
    # FIXME: This probably goes into separate class to regex etc. only once per video objectorino
    # Create a list from a list or something

    # get list of the languages 1. with generated or 2. without generated based on "Show autogenerated transcript"
    # checkbox when moving this to class, create both manual and generated lists at the start and then just return
    # them on call without fetching them with Api
    transcript_list_manual = []
    transcript_list_generated = []
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    for transcript in transcript_list:
        if transcript.is_generated:
            transcript_list_generated.append(transcript.language_code + " - autogenerated")
        else:
            transcript_list_manual.append(transcript.language_code)
    if data:
        # Return
        return transcript_list_manual + transcript_list_generated
    else:
        return transcript_list_manual


def show_autogenerated_transcripts(data):
    # FIXME: This probably goes into separate class to regex etc. only once per video objectorino
    # of course as an object method when creating the object. I think.
    # method will created boolean option to get generated or manual transcript
    # TODO: Merge this with get_list_of_available_languages function!
    # for now this is "fine"
    get_video_id(dpg.get_value("youtubethingy"))
    video_id = get_video_id(dpg.get_value("youtubethingy"))
    transcript_list_manual = []
    transcript_list_generated = []
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    for transcript in transcript_list:
        if transcript.is_generated:
            transcript_list_generated.append(transcript.language_code + " - autogenerated")
        else:
            transcript_list_manual.append(transcript.language_code)

    if data:
        # Return
        dpg.configure_item("listoflanguages", items=transcript_list_manual + transcript_list_generated)
    else:
        dpg.configure_item("listoflanguages", items=transcript_list_manual)


def clear_widgets():
    # Thumbnail, Transcript, listbox
    if "transcript_txt" in dpg.get_aliases():
        dpg.delete_item("transcript_txt")
    dpg.configure_item("listoflanguages", items=[])
    dpg.delete_item("thumbnail_drawlist", children_only=True)


def do_the_youtube_thingy(sender):
    # TODO clean this up! the original function that got truncated
    # FIXME Truncate more!

    # FIXME Write a validator function so stuff are more "coherent"
    video_id = get_video_id(dpg.get_value("youtubethingy"))
    if validate_youtube_video_id_url(video_id):
        # 0. Clear widgets if they exist
        if sender == "youtubethingy" or "youtubethingy_buttons":
            clear_widgets()
        else:
            pass
        # 1. Get videoid and list of languages
        video_id = get_video_id(dpg.get_value("youtubethingy"))
        show_autogenerated_transcripts(dpg.get_value("autogenerated_chkbx"))
        # 2. Get Thumbnail
        get_thumbnail_youtube(video_id, "mq")
        import_img_to_texture_registry(video_id)
        # 3. Check timestamps checkbox to print into transcript video and
        # draw transcript
        draw_transcript("do_the_youtube_thingy", dpg.get_value("listoflanguages"))
    else:
        pass


def get_transcript(data, video_id):
    # Check for selected language or load default one. At click of the langugage on list
    # reload transcript loaded in window

    # FIXME: Move this to class, get all? transcripts or default one (user setting?) at creating
    if "generated" in data:
        language_codes = data[:2]
        transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_generated_transcript(
            [language_codes]).fetch()
    else:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[data, ])
    return transcript


def draw_transcript(sender, data):
    # FIXME: !Clean up por favor!
    video_id = get_video_id(dpg.get_value("youtubethingy"))
    transcript = get_transcript(dpg.get_value("listoflanguages"), video_id)
    paragraph = ""
    if dpg.get_value("timestamps_chkbx"):
        for lines in transcript:
            time = int(lines["start"])
            minutes = '{:0>2}'.format(int(time / 60))
            seconds = '{:0>2}'.format(time % 60)
            if data == "html":
                paragraph = f"{paragraph}<p>{minutes}:{seconds} {lines['text']}</p>\n"
            else:
                paragraph = f"{paragraph}{minutes}:{seconds} {lines['text']}\n"
    else:
        # Hackish solution to get working HTML "string" to put into epub
        # FIXME: Add proper "htmlify" function to get better html
        if data == "html":
            for lines in transcript:
                paragraph = f"{paragraph}<p>{lines['text']}<br>\n"
        else:
            for lines in transcript:
                paragraph = f"{paragraph}{lines['text']}\n"

    if sender == "create_file":
        return paragraph
    else:
        # I think there is a better way :^)
        if "transcript_txt" in dpg.get_aliases():
            dpg.delete_item("transcript_txt")
            dpg.add_text(paragraph, tag="transcript_txt", parent="Transcript")
        else:
            dpg.add_text(paragraph, tag="transcript_txt", parent="Transcript")


def change_button_txt_file_btn_data():
    dpg.configure_item("txt_file_btn", label=f"Create {dpg.get_value('file_format_menu')} file from transcript")


def load_gui():
    dpg.create_context()

    with dpg.window(pos=[0, 0], autosize=True, no_collapse=True, no_resize=True, no_close=True, no_move=True,
                    no_title_bar=True, tag="Primary Window"):
        dpg.bind_font(font1)
        with dpg.group(horizontal=True):
            with dpg.child_window(width=645, tag="youtube_link", border=False):
                # TODO insert input_text automagicaly from clipboard
                dpg.add_text("Youtube URL:")
                with dpg.group(horizontal=True, width=0):
                    dpg.add_input_text(tag="youtubethingy", callback=do_the_youtube_thingy, on_enter=True, width=523)
                    dpg.add_button(tag="youtubethingy_buttons", label="Get transcript", callback=do_the_youtube_thingy)
                dpg.add_text("List of languages:")
                dpg.add_listbox(tag="listoflanguages", callback=draw_transcript, width=623)
                # dpg.add_button(label="Do the youtube thing", callback=do_the_youtube_thing)
                with dpg.group(horizontal=True):
                    with dpg.group(width=335):
                        dpg.add_text("Cover:")
                        with dpg.child_window(tag="thumbnail_drawlist", width=330, height=198, border=True):
                            dpg.add_text(label="placeholder", show=False)
                    with dpg.group(horizontal=True, width=265):
                        with dpg.child_window(tag="settings_drawlist", height=198, width=100, border=False):
                            dpg.add_text("Settings")
                            dpg.add_checkbox(tag="autogenerated_chkbx", label="Show autogenerated transcripts",
                                             callback=do_the_youtube_thingy)
                            dpg.add_checkbox(tag="timestamps_chkbx", label="Add timestamps",
                                             callback=do_the_youtube_thingy)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Format:")
                                dpg.add_combo(("EPUB", "TXT"), default_value="TXT",
                                              callback=change_button_txt_file_btn_data, tag="file_format_menu",
                                              width=100)
                with dpg.group(horizontal=True, width=0):
                    dpg.add_button(tag="txt_file_btn",
                                   label=f"Create {dpg.get_value('file_format_menu')} file from the transcript",
                                   callback=create_a_file, height=50, width=623)

            with dpg.child_window(tag="Transcript", width=445):
                dpg.add_text("Transcript: ")

    dpg.create_viewport(title="Create ebook from Youtube video transcript", width=1113, height=442, resizable=False)

    dpg.set_viewport_small_icon("resources/transcript_to_ebook.ico")
    dpg.set_viewport_large_icon("resources/transcript_to_ebook.ico")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    load_gui()


if __name__ == "__main__":
    main()
