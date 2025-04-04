from collections import deque
from song import Song, SongSection
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

    def get_song_name(self) -> str:
        return self.song.get_name()
        
    def set_song_name(self, name: str):
        self.song.set_name(name)

    def get_song_theme(self) -> str:
        return self.song.get_theme()
    
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
        song_theme = song_theme_json["theme"]
        if self.debug:
            print(f"generated song theme:\n{str(song_theme)}")

        self.song.theme = song_theme
        return song_theme

    def clear_song_theme(self):
        self.song.theme = ""

    def can_generate_lyrics(self) -> bool:
        return len(self.get_song_name()) > 0 and len(self.get_song_theme()) > 0

    def has_lyrics(self) -> bool:
        return self.song.has_lyrics()

    def generate_lyrics(self):
        if self.can_generate_lyrics():
            if self.debug:
                print("Generating Lyrics")

            lyrics = self.model.generate_song(self.get_song_name(), self.get_song_theme())
            self.song.set_lyrics(lyrics=lyrics)

    def export_lyrics(self) -> str:
        return self.song.export_lyrics()


if __name__ == "__main__":
    song_generator = SongGenerator()
    song_generator.set_random_song_name()
    song_generator.set_random_song_theme()
    print(song_generator.get_song_name())
    print(song_generator.get_song_theme())
    song_generator.generate_lyrics()
    print(song_generator.song.export_lyrics())
    

