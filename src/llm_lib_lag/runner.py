import re
import time

from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from .fetchers import fetch_version_date
from .models import (
    LLMConfig,
    EvaluationRun,
    LibraryIdentifier,
    TechVersionGroundTruth,
)


def initialize_llm(llm_config: LLMConfig) -> BaseChatModel:
    """
    Returns an instance of a LangChain-compatible chat model
    given an LLMConfig.

    :param llm_config: The config specifying LLM provider and model name.
    :return: A BaseChatModel instance for inference.
    """
    from langchain_fireworks import ChatFireworks
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_mistralai.chat_models import ChatMistralAI
    from langchain_openai import ChatOpenAI

    match llm_config.provider:
        case "openai":
            return ChatOpenAI(model=llm_config.model, temperature=0)
        case "google":
            return ChatGoogleGenerativeAI(model=llm_config.model, temperature=0)
        case "mistralai":
            return ChatMistralAI(model_name=llm_config.model, temperature=0)
        case "fireworks":
            return ChatFireworks(model=llm_config.model, temperature=0)
        case "anthropic":
            return ChatAnthropic(name=llm_config.model, temperature=0)  # type: ignore

    raise ValueError(f"Provider {llm_config.provider} not supported")


def run_single_evaluation(
    llm_config: LLMConfig,
    ground_truth: TechVersionGroundTruth,
    prompt: ChatPromptTemplate,
    version_regex: str,
) -> EvaluationRun:
    """
    Executes a single evaluation run:

    1. Initializes the specified LLM.
    2. Passes the ground_truth technology name into the prompt.
    3. Parses the LLM output to extract a version string, if any.
    4. Returns an EvaluationRun object.

    :param llm_config: Which LLM provider and model to use.
    :param ground_truth: The ground truth version info (tech + version).
    :param prompt: A ChatPromptTemplate for "What is the latest stable version of X?"
    :param version_regex: Regex to extract a semantic version from the LLM output.
    :return: An EvaluationRun capturing the LLM's response and performance.
    """
    print(f"Ground truth: {ground_truth.tech} - {ground_truth.version}")

    llm = initialize_llm(llm_config)
    chain = prompt | llm | StrOutputParser()  # type: ignore

    start_time = time.time()
    query_input = ground_truth.tech.name
    result_str = chain.invoke({"software_name": query_input})  # type: ignore
    elapsed = time.time() - start_time

    matches = re.finditer(version_regex, result_str)
    versions = [match.group(1) for match in matches]

    if len(versions) > 1:
        raise ValueError(
            f"Multiple versions found in LLM response for {query_input}: {versions}"
        )

    parsed_version = versions[0] if versions else None

    print(f"{llm_config.provider}/{llm_config.model}: {parsed_version or result_str}")

    if (
        parsed_version
        and ground_truth.release_date
        and isinstance(ground_truth.tech, LibraryIdentifier)
    ):
        try:
            parsed_version_date = fetch_version_date(ground_truth.tech, parsed_version)
            lag_days = (ground_truth.release_date - parsed_version_date.date()).days
            parsed_version_exists = True
        except Exception as e:
            print(f"Error fetching version date: {e}")
            lag_days = None
            parsed_version_exists = False
        print(f"Lag days: {lag_days}")
    else:
        lag_days = None
        parsed_version_exists = None

    run = EvaluationRun(
        ground_truth=ground_truth,
        llm_config=llm_config,
        output=result_str,
        parsed_version=parsed_version,
        parsed_version_exists=parsed_version_exists,
        execution_time_seconds=elapsed,
        lag_days=lag_days,
    )

    print(
        f"Run: {ground_truth.tech} - {llm_config.provider}/{llm_config.model} - {parsed_version}"
    )

    return run
