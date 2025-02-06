import os
import re
import time

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr
from src.models import EvaluationRun, LLMConfig


from src.ground_thruths import GROUND_TRUTHS

load_dotenv()


LLMS = [
    LLMConfig(provider="openai", model="gpt-4o-mini"),
    LLMConfig(provider="google", model="gemini-1.5-flash"),
    LLMConfig(provider="google", model="gemini-2.0-flash-001"),
    LLMConfig(provider="google", model="gemini-2.0-flash-lite-preview-02-05"),
    LLMConfig(provider="mistralai", model="mistral-small-2501"),  # small-v3
    LLMConfig(
        provider="fireworks",
        model="accounts/fireworks/models/qwen2p5-coder-32b-instruct",
    ),
    LLMConfig(provider="fireworks", model="accounts/fireworks/models/deepseek-v3"),
]


def initialize_llm(llm: LLMConfig) -> BaseChatModel:
    match llm.provider:
        case "openai":
            return ChatOpenAI(model=llm.model, temperature=0)
        case "google":
            return ChatGoogleGenerativeAI(model=llm.model, temperature=0)
        case "mistralai":
            return ChatMistralAI(model_name=llm.model, temperature=0)
        case "fireworks":
            return ChatFireworks(model=llm.model, temperature=0)

    raise ValueError(f"Provider {llm.provider} not supported")


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

RUNS_FILE = "runs.jsonl"


def _execute():
    with open(RUNS_FILE, "a") as f:
        for gt in GROUND_TRUTHS:
            print(f"{gt.software_name} - {gt.version}")

            for llm_config in LLMS:
                llm = initialize_llm(llm_config)

                t1 = time.time()

                chain = prompt | llm | StrOutputParser()
                result_str = chain.invoke({"software_name": gt.software_name})
                t2 = time.time()

                # extract version from result using regex
                version = re.search(version_regex, result_str)
                if not version:
                    print(f"{llm_config.provider}/{llm_config.model}: {result_str}")
                    parsed_version = None
                else:
                    parsed_version = version.group(1)

                print(f"{llm_config.provider}/{llm_config.model}: {parsed_version}")

                run = EvaluationRun(
                    ground_truth=gt,
                    llm_config=llm_config,
                    output=result_str,
                    parsed_version=parsed_version,
                    execution_time_seconds=t2 - t1,
                )

                f.write(run.model_dump_json() + "\n")

            print("-" * 100)


if __name__ == "__main__":
    _execute()
