from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

import yaml
import json
import os


MODELS = ["gemma3:1b", "gemma3:12b", "qwen2.5-coder:7b", "deepseek-r1:14b"]


def generate_feature(model, section_name, feature_name, filename):
    # Get the LLM instance
    llm = ChatOllama(
        model=model,
        #temperature=0.4,
        #top_p=0.95,
        #max_tokens=10000
    )

    # and load the prompts from the YAML file
    with open("prompts.yaml", "r") as prompts_file:
        prompts = yaml.safe_load(prompts_file)

    # get the system prompt
    system_prompt = prompts["system_prompt"]

    # build the prompt
    prompt = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"from {section_name}, write an article about the new functionality for the modern c++ topic: {feature_name}")
    ]

    response = llm.invoke(prompt)

    with open(filename, "w") as file:
        file.write(response.content)


def generate_all_features_for_model(model, data, max_features=0):
        feature_count = 0
        model_name = model.replace(":", "_")
        # iterate over the sections and features
        for section in data.items():
            section_name = f"output/{model_name}/{section[0]}"

            for feature in section[1].items():
                # check if we reached the maximum number of features
                if max_features > 0 and feature_count >= max_features:
                    return

                # create the model folder if it does not exist
                #if not os.path.exists(model_name):
                #    os.makedirs(model_name)

                # create the section folder if it does not exist
                if not os.path.exists(section_name):
                    os.makedirs(section_name)

                # generate the filename and the feature name
                filename = feature[0]
                feature_name = feature[1]
                filename = f"{section_name}/{filename}.md"

                # generate the feature
                print(f'Generating {filename} for "{feature_name}"')
                generate_feature(model, section_name, feature_name, filename)
                feature_count += 1


def generate_all_features(max_features=0):
    # open the features file and read the data from it with json
    with open("features.json", "r") as file:
        data = json.load(file)

    # generate the features for each model
    for model in MODELS:
        print(f"Generating features for {model}")
        generate_all_features_for_model(model, data, max_features)


# generate all features
if __name__ == "__main__":
    generate_all_features(1)
