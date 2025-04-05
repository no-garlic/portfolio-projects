import streamlit as st
import streamlit_antd_components as sac
import streamlit_utils as st_utils
from song_generator import SongGenerator
import json

class LyricsGeneratorApp:
    def __init__(self):
        """
        Initialize the Application.
        """
        if "song_generator" not in st.session_state:
            st.session_state["song_generator"] = SongGenerator()


    def debug_load_from_file(self, path="songs", filename = ""):
        song_generator = st.session_state["song_generator"]
        song_generator.debug_load_from_file(path, filename)
        #song_generator.clear_lyrics()


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

                        song_generator.generate_lyrics()
                        st.rerun()


    def edit_song(self):
        song_generator = st.session_state["song_generator"]
        song_structure = song_generator.get_song_structure()

        text : str
        text = song_structure.replace("[", "").replace("]", "").replace("\n", ",").replace(",,", ",").replace(",@", ":@")
        
        control_id = 0

        tokens = text.split(",")
        for token in tokens:
            if ":" in token:
                label, section = token.split(":")
                lyrics = song_generator.get_section_lyrics(section)

                with st.container(border=True):
                    st.markdown(f"##### {label}")
                    st.text(lyrics)
            else:
                with st.container(border=True):             #TODO: Change to st_horizontal with right justification
                    content, actions = st.columns([5, 1])
                    with content:
                        st.markdown(f"##### {token}")
                    with actions:
                        with st.popover("Actions"):
                            k=str(control_id)
                            sac.menu(
                                [
                                    sac.MenuItem("home"),
                                    sac.MenuItem("next")
                                ], index=-1, key=k
                            )
                            control_id += 1


                            #st.button("Edit", key=f"edit{control_id}")
                            #control_id += 1
                            #st.button("Generate New", key=f"edit{control_id}")
                            #control_id += 1
                            




        #song_lyrics = song_generator.get_lyrics()

        #st.text(json.dumps(song_lyrics, indent=4))


        #formatted_lyrics = song_generator.export_lyrics()
        #st.markdown(f"### {song_generator.get_song_name()}")
        #st.text(formatted_lyrics)


if __name__ == "__main__":
    app = LyricsGeneratorApp()
    app.debug_load_from_file("songs", "shine_bright.json")
    app.streamlit_main(subpage=False)
