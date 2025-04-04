import streamlit as st
import streamlit_utils as st_utils
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
            st.header("Song Lyrics Generator")

        song_generator = st.session_state["song_generator"]
        if song_generator.has_lyrics():
            self.edit_song()
        else:
            self.prepare_song()
                
        
    def prepare_song(self):
        song_generator = st.session_state["song_generator"]

        if len(song_generator.get_song_name()) > 0:
            st.success('Enter the name of your song or click Random to generate one', icon="✅")
        else:
            st.info('Enter the name of your song or click Random to generate one', icon="ℹ️")

        txt_song_name = st.text_input(label="Song Name", value=song_generator.get_song_name(), help="Enter the name for your song.")
        if txt_song_name != song_generator.get_song_name():
            song_generator.set_song_name(txt_song_name)
            song_generator.clear_song_theme()

        with st_utils.horizontal():
            if st.button("Random", key="song_name_button"):
                with st.spinner("Generating...", show_time=True):
                    song_generator.clear_song_theme()
                    song_generator.set_random_song_name()
                    st.rerun()

        if len(song_generator.get_song_name()) == 0:
            song_generator.clear_song_theme()
        else:
            st.markdown("#### ")

            if len(song_generator.get_song_theme()) > 0:
                st.success('Enter the theme of your song or click Random to generate one', icon="✅")
            else:
                st.info('Enter the theme of your song or click Random to generate one', icon="ℹ️")
            
            #TODO - break the theme into 3 sections, in the json there should be 3 keys
            # show it as 3 paragraphs with a line space between each
            # but combine it into a single paragraph when passing it to the model for lyrics generation

            txt_song_theme = st.text_area(label="Song Theme", value=song_generator.get_song_theme(), help="Enter the theme for your song", height=280)
            song_generator.set_song_theme(txt_song_theme)

            with st_utils.horizontal():
                if st.button("Random", key="song_theme_button"):
                    with st.spinner("Generating...", show_time=True):
                        song_generator.set_random_song_theme()
                        st.rerun()
                    
        if len(song_generator.get_song_name()) > 0 and len(song_generator.get_song_theme()) > 0:
            
            st.markdown("#### ")
            st.info('When you are happy with your song name and theme, generate your lyrics', icon="ℹ️")
            
            with st_utils.horizontal():
                if st.button("Generate Song Lyrics", key="song_lyrics_button"):
                    with st.spinner("Generating...", show_time=True):

                        #TODO need to trim the song lyrics
                        #TODO need to put lyrics sections into containers (expanders?)
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
