import yaml
import json
from pprint import pprint
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


class Model:
    def __init__(self, debug=False):
        load_dotenv()
        with open("prompts.yaml", "r") as prompts_file:
            self.prompts = yaml.safe_load(prompts_file)
        self.role = self.prompts["role"]        

        #self.llm = ChatOllama(model="gemma3:4b", format="json", temperature="0.9")

        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        self.debug = debug


    def generate_template(self, prompt_name: str) -> str:
        prompt = self.prompts[prompt_name]
        full_prompt = f"{self.role}\n\n{prompt}\n"
        return full_prompt


    def invoke_llm(self, prompt: str) -> dict:

        if self.debug:
            print(f"\n----- INVOKING LLM -----\n{prompt}\n")

        response = self.llm.invoke(prompt)
        response_content = response.content.replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", "'").replace("\u201d", "'").replace("…", "...")

        if self.debug:
            print(f"\n----- LLM RESPONSE (RAW) CONTENT -----\n{response.content}\n")

        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            return {"error": "Failed to parse LLM response as JSON"}
        

    def generate_song_names(self, count=20, history="") -> dict:
        template = self.generate_template("song_names")
        if not history or len(history) == 0:
            history = "Neon"
        prompt_template = PromptTemplate(template=template, input_variables=["count", "history"])
        prompt = prompt_template.format(count=count, history=history)

        response = self.invoke_llm(prompt)
        return response


    def generate_song_theme(self, song_name: str) -> dict:
        template = self.generate_template("song_theme")
        propmt_template = PromptTemplate(template=template, input_variables="song_name")
        prompt = propmt_template.format(song_name=song_name)

        response = self.invoke_llm(prompt)
        return response


    def generate_song(self, song_name: str, song_theme: str) -> dict:
        template = self.generate_template("full_song")
        propmt_template = PromptTemplate(template=template, input_variables=["song_name", "song_theme"])
        prompt = propmt_template.format(song_theme=song_theme, song_name=song_name)

        response = self.invoke_llm(prompt)
        return response


if __name__ == "__main__":
    model = Model(debug=True)

    song_name_json = model.generate_song_names(count=5)
    print("\n----- SONG NAMES -----\n")
    print(json.dumps(song_name_json, indent=4))
    song_name = song_name_json["song1"]

    song_theme_json = model.generate_song_theme(song_name=song_name)
    print("\n----- SONG THEME -----\n")
    print(json.dumps(song_theme_json, indent=4))
    song_theme = song_theme_json["theme"]

    song = model.generate_song(song_name=song_name, song_theme=song_theme)
    print("\n----- SONG -----\n")
    print(song)
    print(json.dumps(song, indent=4))

