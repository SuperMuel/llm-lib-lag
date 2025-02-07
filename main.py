import re
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from llm_lib_lag.models import LLMConfig
from llm_lib_lag.ground_thruths import GROUND_TRUTHS
from llm_lib_lag.runner import run_single_evaluation
from llm_lib_lag.evaluation import evaluate_runs
from llm_lib_lag.io_utils import load_runs_from_jsonl, get_missing_runs

load_dotenv()

# ------------------------------------------------------
# Globals & Constants
# ------------------------------------------------------
RUNS_FILE = "runs.jsonl"

LLMS = [
    LLMConfig(provider="openai", model="gpt-4o-mini"),
    LLMConfig(provider="google_genai", model="gemini-1.5-flash"),
    LLMConfig(provider="google_genai", model="gemini-2.0-flash-001"),
    LLMConfig(provider="google_genai", model="gemini-2.0-flash-lite-preview-02-05"),
    LLMConfig(provider="mistralai", model="mistral-small-2501"),
    LLMConfig(provider="anthropic", model="claude-3-5-haiku-20241022"),
    LLMConfig(
        provider="fireworks",
        model="accounts/fireworks/models/qwen2p5-coder-32b-instruct",
    ),
    LLMConfig(provider="fireworks", model="accounts/fireworks/models/deepseek-v3"),
]

# Reusable prompt for "latest stable version"
VERSION_PROMPT = ChatPromptTemplate.from_messages(  # type: ignore
    [
        (
            "system",
            "You are a helpful assistant that can answer questions about the latest version of a software. "
            "You must provide a specific version number in semantic versioning format (e.g., '3.12.1', '5.0.2', '2.31.0'). "
            "Do not use words like 'latest' or 'current' - provide the actual version number.",
        ),
        ("user", "What is the latest stable version of {software_name}?"),
    ]
)

VERSION_REGEX = r"(\d+\.\d+(?:\.\d+)?(?:[-.][A-Za-z0-9]+)*)"

# Sanity check on the regex
assert (
    re.search(VERSION_REGEX, "The latest stable version of Python is **3.12.1**").group(  # type: ignore
        1
    )
    == "3.12.1"
)


# ------------------------------------------------------
# Main CLI Logic
# ------------------------------------------------------
def main() -> None:
    """
    Entry point for evaluating multiple LLMs against ground-truth version data.

    Usage Example:
        python main.py
    """
    # Load existing runs
    runs = load_runs_from_jsonl(RUNS_FILE)

    # Determine which (LLM, TechVersion) combos have not yet been evaluated
    pairs_to_run = [(llm, gt) for llm in LLMS for gt in GROUND_TRUTHS]
    missing = get_missing_runs(pairs_to_run, runs)

    if missing:
        print(f"Executing {len(missing)} new runs...")
    else:
        print("No new runs to execute.")

    # Execute runs for missing pairs
    for llm_config, ground_truth in missing:
        print(f"Running {llm_config.model} for {ground_truth.tech.name}...")
        run = run_single_evaluation(
            llm_config=llm_config,
            ground_truth=ground_truth,
            prompt=VERSION_PROMPT,
            version_regex=VERSION_REGEX,
        )
        runs.append(run)

        # Persist runs to file
        with open(RUNS_FILE, "a") as f:
            f.write(run.model_dump_json() + "\n")
            print(f"Wrote run to {RUNS_FILE}")

    # Evaluate and print results
    evaluate_runs(runs)


if __name__ == "__main__":
    main()
