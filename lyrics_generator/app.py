import streamlit as st
import streamlit_antd_components as sac
from random import Random
from song_generator import SongGenerator


class LyricsGeneratorApp:
    def __init__(self):
        """
        Initialize the Application.
        """
        if "song_generator" not in st.session_state:
            st.session_state["song_generator"] = SongGenerator()


    def streamlit_main(self, subpage=False):
        """
        Main function to run the Streamlit app.
        """
        # set the page title and header unless this is a subpage
        if not subpage:
            st.set_page_config(page_title="Lyrics Generator")
            st.header("Lyrics Generator")

            song_generator = st.session_state["song_generator"]
            if song_generator.has_lyrics():
                self.edit_song()
            else:
                self.prepare_song()
                
        
    def prepare_song(self):
        song_generator = st.session_state["song_generator"]

        txt_song_name = st.text_input(label="Song Name", value=song_generator.get_song_name(), help="Enter the name for your song.")
        if txt_song_name != song_generator.get_song_name():
            song_generator.set_song_name(txt_song_name)
            song_generator.clear_song_theme()

        if st.button("Generate Song Name", key="song_name_button"):
            song_generator.clear_song_theme()
            song_generator.set_random_song_name()
            st.rerun()

        if len(song_generator.get_song_name()) == 0:
            song_generator.clear_song_theme()
        else:
            txt_song_theme = st.text_area(label="Song Theme", value=song_generator.get_song_theme(), help="Enter the theme for your song", height=250)
            song_generator.set_song_theme(txt_song_theme)

            if st.button("Generate Song Theme", key="song_theme_button"):
                song_generator.set_random_song_theme()
                st.rerun()

        if len(song_generator.get_song_name()) > 0 and len(song_generator.get_song_theme()) > 0:
            st.markdown("---")
            if st.button("Generate Song Lyrics", key="song_lyrics_button"):
                song_generator.generate_lyrics()
                st.rerun()


    def edit_song(self):
        song_generator = st.session_state["song_generator"]

        lyrics = song_generator.export_lyrics()
        st.markdown(f"### {song_generator.get_song_name()}")
        st.text(lyrics)


if __name__ == "__main__":
    app = LyricsGeneratorApp()
    app.streamlit_main(subpage=False)
