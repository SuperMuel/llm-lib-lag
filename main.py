import json
import os
from packaging.version import parse, Version
import re
import time
from typing import Sequence

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


def evaluate_runs(runs: Sequence[EvaluationRun]) -> None:
    """
    Evaluates a list of EvaluationRun objects, compares the LLM responses
    to the ground truths, and prints evaluation metrics.

    Args:
        runs: A list of EvaluationRun objects.
    """

    if not runs:
        print("No evaluation runs provided.")
        return

    total_runs = len(runs)
    exact_matches = 0
    major_matches = 0
    minor_matches = 0
    total_execution_time = 0.0

    # Group runs by software and LLM for more detailed analysis
    by_software: dict[str, list[EvaluationRun]] = {}
    by_llm: dict[str, list[EvaluationRun]] = {}

    for run in runs:
        software_name = run.ground_truth.software_name
        llm_key = f"{run.llm_config.provider}/{run.llm_config.model}"

        if software_name not in by_software:
            by_software[software_name] = []
        by_software[software_name].append(run)

        if llm_key not in by_llm:
            by_llm[llm_key] = []
        by_llm[llm_key].append(run)

        total_execution_time += run.execution_time_seconds

        if run.parsed_version:
            try:
                gt_version = parse(run.ground_truth.version)
                response_version = parse(run.parsed_version)

                if gt_version == response_version:
                    exact_matches += 1
                if gt_version.major == response_version.major:
                    major_matches += 1
                if (
                    gt_version.major == response_version.major
                    and gt_version.minor == response_version.minor
                ):
                    minor_matches += 1
            except Exception as e:
                print(f"Error parsing version for {software_name} ({llm_key}): {e}")

    print("-" * 50)
    print("Overall Evaluation Results:")
    print(f"Total Runs: {total_runs}")
    print(f"Exact Matches: {exact_matches} ({exact_matches / total_runs:.2%})")
    print(f"Major Version Matches: {major_matches} ({major_matches / total_runs:.2%})")
    print(f"Minor Version Matches: {minor_matches} ({minor_matches / total_runs:.2%})")
    print(f"Average Execution Time: {total_execution_time / total_runs:.2f} seconds")
    print("-" * 50)

    print("\nResults by Software:")
    for software_name, software_runs in by_software.items():
        print(f"\n  {software_name}:")
        software_total = len(software_runs)
        software_exact = 0
        software_major = 0
        software_minor = 0

        for run in software_runs:
            if run.parsed_version:
                try:
                    gt_version = parse(run.ground_truth.version)
                    response_version = parse(run.parsed_version)

                    if gt_version == response_version:
                        software_exact += 1
                    if gt_version.major == response_version.major:
                        software_major += 1
                    if (
                        gt_version.major == response_version.major
                        and gt_version.minor == response_version.minor
                    ):
                        software_minor += 1
                except Exception as e:
                    print(
                        f"Error parsing version for {software_name} ({run.llm_config.provider}/{run.llm_config.model}): {e}"
                    )

        print(f"    Total Runs: {software_total}")
        print(
            f"    Exact Matches: {software_exact} ({software_exact / software_total:.2%})"
        )
        print(
            f"    Major Matches: {software_major} ({software_major / software_total:.2%})"
        )
        print(
            f"    Minor Matches: {software_minor} ({software_minor / software_total:.2%})"
        )

    print("\nResults by LLM:")
    for llm_key, llm_runs in by_llm.items():
        print(f"\n  {llm_key}:")
        llm_total = len(llm_runs)
        llm_exact = 0
        llm_major = 0
        llm_minor = 0
        llm_total_time = 0.0

        for run in llm_runs:
            llm_total_time += run.execution_time_seconds
            if run.parsed_version:
                try:
                    gt_version = parse(run.ground_truth.version)
                    response_version = parse(run.parsed_version)
                    if gt_version == response_version:
                        llm_exact += 1
                    if gt_version.major == response_version.major:
                        llm_major += 1
                    if (
                        gt_version.major == response_version.major
                        and gt_version.minor == response_version.minor
                    ):
                        llm_minor += 1
                except Exception as e:
                    print(
                        f"Error parsing version for {run.ground_truth.software_name} ({llm_key}): {e}"
                    )

        print(f"    Total Runs: {llm_total}")
        print(f"    Exact Matches: {llm_exact} ({llm_exact / llm_total:.2%})")
        print(f"    Major Matches: {llm_major} ({llm_major / llm_total:.2%})")
        print(f"    Minor Matches: {llm_minor} ({llm_minor / llm_total:.2%})")
        print(f"    Average Execution Time: {llm_total_time / llm_total:.2f} seconds")


def load_runs_from_jsonl(filepath: str) -> list[EvaluationRun]:
    """Loads evaluation runs from a JSON Lines file."""
    runs = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                try:
                    run_data = json.loads(line)
                    run = EvaluationRun(**run_data)
                    runs.append(run)
                except Exception as e:
                    print(f"Error parsing run data: {e} \n {line=}")

    except FileNotFoundError:
        print(f"Error: Runs file not found: {filepath}")
        return []  # Return an empty list if the file doesn't exist
    return runs


if __name__ == "__main__":
    # _execute()
    runs = load_runs_from_jsonl(RUNS_FILE)
    evaluate_runs(runs)
