from collections import deque
from song import Song
from model import Model


class SongGenerator:
    def __init__(self, debug=False):
        self.model = Model()
        self.song = Song()
        self.random_song_names = deque()
        self.song_name_history = list()
        self.debug = debug
        if self.debug:
            print("creating a new song generator")

    def debug_load_from_file(self, path="songs", filename=""):
        if len(filename) > 0:
            self.song.load_from_file(path, filename)


    def get_song_name(self) -> str:
        return self.song.get_name()
        
    def set_song_name(self, name: str):
        self.song.set_name(name)

    def get_song_theme(self, single_paragraph=False) -> str:
        song_theme = self.song.get_theme()
        if single_paragraph:
            song_theme = song_theme.replace("\n\n", " ").replace("\n", " ")
        return song_theme
    
    def set_song_theme(self, theme: str):
        self.song.set_theme(theme)

    def set_random_song_name(self) -> str:
        if len(self.random_song_names) == 0:
            if self.debug:
                print("llm -> generate new song names...")

            song_name_history = ", ".join(map(str, self.song_name_history))
            song_names = self.model.generate_song_names(5, song_name_history)
            
            if self.debug:
                print(f"generated song names:\n{song_names.values()}")

            self.random_song_names.extend(song_names.values())
            self.song_name_history.append(song_names.values())

        song_name = self.random_song_names.popleft()
        self.song.name = song_name
        if self.debug:
            print(f"setting random song name: {song_name}")
        return song_name
    
    def set_random_song_theme(self) -> str:
        if self.debug:
            print("llm -> generate new song theme...")

        song_theme_json = self.model.generate_song_theme(self.get_song_name())
        song_theme_description = song_theme_json["description"]
        song_theme_narrative1 = song_theme_json["narrative1"]
        song_theme_narrative2 = song_theme_json["narrative2"]
        song_theme_mood = song_theme_json["mood"]
        song_theme = f"{song_theme_description}\n\n{song_theme_narrative1} {song_theme_narrative2}\n\n{song_theme_mood}"
        
        if self.debug:
            print(f"generated song theme:\n{str(song_theme)}")

        self.song.theme = song_theme
        return song_theme

    def clear_song_theme(self):
        self.song.theme = ""

    def get_song_structure(self) -> str:
        return self.song.get_song_structure()

    def clear_lyrics(self):
        self.song.set_lyrics({})

    def can_generate_lyrics(self) -> bool:
        return len(self.get_song_name()) > 0 and len(self.get_song_theme()) > 0

    def has_lyrics(self) -> bool:
        return self.song.has_lyrics()

    def generate_lyrics(self):
        if self.can_generate_lyrics():
            if self.debug:
                print("Generating Lyrics")

            lyrics = self.model.generate_song(self.get_song_name(), self.get_song_theme(single_paragraph=True))
            self.song.set_lyrics(lyrics=lyrics)
            self.song.save_to_file()

    def get_lyrics(self) -> dict:
        return self.song.get_lyrics()

    def get_section_lyrics(self, section_name: str) -> str:
        return self.song.get_section_lyrics(section_name)

    def set_section_lyrics(self, section_name: str, lyrics: str):
        self.song.set_section_lyrics(section_name, lyrics)

    def export_lyrics(self) -> str:
        return self.song.export_lyrics()


if __name__ == "__main__":
    song_generator = SongGenerator()
    song_generator.set_random_song_name()
    song_generator.set_random_song_theme()
    song_generator.generate_lyrics()

    print("-------- SONG NAME --------")
    print(song_generator.get_song_name())
    print("-------- SONG THEME (FORMATTED) --------")
    print(song_generator.get_song_theme(single_paragraph=False))
    print("-------- SONG NAME (COMPRESSED) --------")
    print(song_generator.get_song_theme(single_paragraph=True))
    print("-------- SONG LYRICS --------")
    print(song_generator.song.export_lyrics())
    