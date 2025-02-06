from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel
from pydantic import BaseModel, Field

from dotenv import load_dotenv

from src.ground_thruths import GROUND_TRUTHS

load_dotenv()

LLMS = [
    ("openai", "gpt-4o-mini"),
    ("google", "gemini-1.5-flash"),
]


def initialize_llm(provider: str, model: str) -> BaseChatModel:
    match provider:
        case "openai":
            return ChatOpenAI(model=model, temperature=0)
        case "google":
            return ChatGoogleGenerativeAI(model=model, temperature=0)

    raise ValueError(f"Provider {provider} not supported")


class SoftwareVersionInfo(BaseModel):
    version: str = Field(
        ..., description="The version string (e.g., '3.12.1', '5.0.2', '2.31.0')"
    )
    # release_date: date


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that can answer questions about the latest version of a software.",
        ),
        ("user", "What is the latest stable version of {software_name}?"),
    ]
)


def _eval_test():
    for gt in GROUND_TRUTHS:
        print(gt)
        for provider, model in LLMS:
            llm = initialize_llm(provider, model)
            chain = prompt | llm.with_structured_output(SoftwareVersionInfo)

            result = chain.invoke({"software_name": gt.software_name})

            print(result)
        print("-" * 100)


if __name__ == "__main__":
    _eval_test()
