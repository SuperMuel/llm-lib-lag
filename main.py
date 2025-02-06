from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from pydantic import BaseModel, Field

from dotenv import load_dotenv

load_dotenv()


class SoftwareVersionInfo(BaseModel):
    version: str = Field(
        ..., description="The version string (e.g., '3.12.1', '5.0.2', '2.31.0')"
    )
    # release_date: date


def eval_test():
    # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant that can answer questions about the latest version of a software.",
            ),
            ("user", "What is the latest stable version of {software_name}?"),
        ]
    )

    chain = prompt | llm.with_structured_output(SoftwareVersionInfo)

    result = chain.invoke({"software_name": "Python"})

    print(result)


if __name__ == "__main__":
    eval_test()
