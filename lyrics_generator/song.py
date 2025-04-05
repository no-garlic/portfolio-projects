import json
import yaml

from model import Model
from pprint import pprint


class Song:
    """
    Represents a song with a structure, name, theme, and lyrics.
    """
    def __init__(self, song_structure="pop_song"):
        self.name = ""
        self.theme = ""
        self.lyrics = {}

        with open("song_structure.yaml", "r") as song_structure_file:
            song_structure_yaml = yaml.safe_load(song_structure_file)
            self.song_structure = song_structure_yaml[song_structure]


    def get_name(self) -> str:
        return self.name


    def set_name(self, name: str):
        self.name = name


    def get_theme(self) -> str:
        return self.theme


    def set_theme(self, theme: str):
        self.theme = theme


    def get_song_structure(self) -> str:
        return self.song_structure


    def set_lyrics(self, lyrics: dict):
        self.lyrics = lyrics


    def get_lyrics(self) -> dict:
        return self.lyrics
    

    def has_lyrics(self) -> bool:
        return len(self.lyrics.keys()) > 0


    def get_section_lyrics(self, section_name: str) -> str:
        section_name_json = section_name.strip("@")
        return self.lyrics[section_name_json].strip()


    def set_section_lyrics(self, section_name: str, lyrics: str):
        section_name_json = section_name.strip("@")
        self.lyrics[section_name_json] = lyrics


    def export_lyrics(self) -> str:
        song_listing = self.song_structure

        #TODO: change [] with a list of sections from the song structure


        for section in []:
            section_name_yaml = section.value
            section_name_json = section.value.strip("@")
            section_lyrics = self.lyrics[section_name_json].strip()
            song_listing = song_listing.replace(section_name_yaml, section_lyrics)

        return song_listing
    
    def save_to_file(self, path = "songs", filename = ""):
        """
        Save the song's name, theme, and lyrics to a JSON file.
        """
        song_data = {
            "name": self.name,
            "theme": self.theme,
            "lyrics": self.lyrics
        }

        if len(filename) == 0:
            filename = self.get_name().replace(" ", "_").lower() + ".json"

        filepath = path + "/" + filename

        with open(filepath, "w") as file:
            json.dump(song_data, file, indent=4)

    def load_from_file(self, path = "songs", filename = ""):
        """
        Load the song's name, theme, and lyrics from a JSON file.
        """
        filepath = path + "/" + filename
        with open(filepath, "r") as file:
            song_data = json.load(file)
            self.name = song_data.get("name", "")
            self.theme = song_data.get("theme", "")
            self.lyrics = song_data.get("lyrics", {})


if __name__ == "__main__":
    model = Model()
    
    song_name = "Dancing At The Beach"
    song_theme = "A song about dancing at night time at the beach"

    lyrics = model.generate_song(song_name=song_name, song_theme=song_theme)

    song = Song()
    song.create(song_name, song_theme, lyrics)
    
    listing = song.export_lyrics()
    print(f"\n----------- FULL SONG -----------\n{listing}")

    chorus = song.get_section_lyrics(SongSection.CHORUS)
    print(f"\n----------- CHORUS -----------\n{chorus}")

    new_chorus = "Hello\nWorld.\nAnd\nBye."
    song.set_section_lyrics(SongSection.CHORUS, new_chorus)

    listing = song.export_lyrics()
    print(f"\n----------- UPDATED SONG -----------\n{listing}")
