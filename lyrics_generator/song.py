import json
import yaml

from enum import StrEnum
from model import Model
from pprint import pprint


class SongSection(StrEnum):
    VERSE1 = "@verse1"
    VERSE2 = "@verse2"
    PRECHORUS = "@prechorus"
    CHORUS = "@chorus"
    BRIDGE = "@bridge"
    OUTRO = "@outro"


class Song:
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


    def set_lyrics(self, lyrics: dict):
        self.lyrics = lyrics


    def get_lyrics(self) -> dict:
        return self.lyrics
    

    def has_lyrics(self) -> bool:
        return len(self.lyrics.keys()) > 0


    def get_section_lyrics(self, section: SongSection) -> str:
        section_name_json = section.value.strip("@")
        return self.lyrics[section_name_json]


    def set_section_lyrics(self, section: SongSection, lyrics: str):
        section_name_json = section.value.strip("@")
        self.lyrics[section_name_json] = lyrics


    def export_lyrics(self) -> str:
        song_listing = self.song_structure

        for section in SongSection:
            section_name_yaml = section.value
            section_name_json = section.value.strip("@")
            song_listing = song_listing.replace(section_name_yaml, self.lyrics[section_name_json])

        return song_listing


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
