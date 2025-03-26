from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

def get_llm(provider="ollama", model="gemma3:4b"):
    provider = provider.lower()

    if provider == "ollama":
        return ChatOllama(model=model)

    if provider == "openai":
        return ChatOpenAI(model_name=model)

    if provider == "anthropic":
        return ChatAnthropic(model_name=model)

    if provider == "google":
        return ChatGoogleGenerativeAI(model=model)

    raise ValueError(f"Model provider: {provider} not found.")
