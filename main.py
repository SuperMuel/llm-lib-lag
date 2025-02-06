import os
import re

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from src.ground_thruths import GROUND_TRUTHS

load_dotenv()

LLMS = [
    ("openai", "gpt-4o-mini"),
    ("google", "gemini-1.5-flash"),
    ("google", "gemini-2.0-flash-001"),
    ("google", "gemini-2.0-flash-lite-preview-02-05"),
    ("mistralai", "mistral-small-2501"),  # small-v3
    # ("fireworks", "accounts/fireworks/models/deepseek-v3"),
    # ("fireworks", "accounts/fireworks/models/qwen2p5-coder-32b-instruct"),
]


def initialize_llm(provider: str, model: str) -> BaseChatModel:
    match provider.lower():
        case "openai":
            return ChatOpenAI(model=model, temperature=0)
        case "google":
            return ChatGoogleGenerativeAI(model=model, temperature=0)
        case "mistralai":
            return ChatMistralAI(model_name=model, temperature=0)
        case "fireworks":
            return ChatFireworks(model=model, temperature=0)

    raise ValueError(f"Provider {provider} not supported")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that can answer questions about the latest version of a software. "
            "You must provide a specific version number in semantic versioning format (e.g., '3.12.1', '5.0.2', '2.31.0'). Do not use words like 'latest' or 'current' - provide the actual version number.",
        ),
        ("user", "What is the latest stable version of {software_name}?"),
    ]
)

version_regex = r"(\d+\.\d+(?:\.\d+)?(?:[-.][A-Za-z0-9]+)*)"

assert (
    re.search(version_regex, "The latest stable version of Python is **3.12.1**").group(  # type: ignore
        1
    )
    == "3.12.1"
)
assert re.match(version_regex, "3.12.1")
assert not re.match(version_regex, "")


def _eval_test():
    for gt in GROUND_TRUTHS:
        print(f"{gt.software_name} - {gt.version}")
        for provider, model in LLMS:
            llm = initialize_llm(provider, model)

            chain = prompt | llm | StrOutputParser()
            result = chain.invoke({"software_name": gt.software_name})

            # extract version from result using regex
            version = re.search(version_regex, result)
            if not version:
                print(f"{provider}/{model}: {result}")
                continue
            version = version.group(1)

            print(f"{provider}/{model}: {version}")
        print("-" * 100)


if __name__ == "__main__":
    _eval_test()
