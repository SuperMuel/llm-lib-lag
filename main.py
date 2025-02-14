import re
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from llm_lib_lag.models import LLMConfig
from llm_lib_lag.ground_truths import GROUND_TRUTHS
from llm_lib_lag.runner import run_single_evaluation
from llm_lib_lag.evaluation import evaluate_runs
from llm_lib_lag.io_utils import load_runs_from_jsonl, get_missing_runs
from tqdm import tqdm
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------
# Logging Configuration
# ------------------------------------------------------
def setup_logging(log_level: int = logging.INFO) -> None:
    """Configure logging to both file and console with proper formatting."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"llm_lib_lag_{timestamp}.log"

    # Create formatters and handlers
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    console_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Quiet some chatty libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

# ------------------------------------------------------
# Globals & Constants
# ------------------------------------------------------
RUNS_FILE = "runs.jsonl"

LLMS = [
    LLMConfig(provider="openai", model="gpt-4o-mini"),
    LLMConfig(provider="openai", model="o3-mini-2025-01-31"),
    LLMConfig(provider="openai", model="gpt-4o-2024-08-06"),
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
    LLMConfig(provider="perplexity", model="sonar"),
    LLMConfig(provider="groq", model="deepseek-r1-distill-qwen-32b"),
]

# Reusable prompt for "latest stable version"
VERSION_PROMPT = ChatPromptTemplate.from_messages(  # type: ignore
    [
        (
            "system",
            """You are a helpful assistant that can answer questions about the latest version of a software. 

You must provide a specific version number in semantic versioning format (e.g., '3.12.1', '5.0.2', '2.31.0'). 

Do not use words like 'latest' or 'current' - provide the actual version number. 

Write your reasoning in <thinking> tags.
Output your final answer for the latest version inside <answer> tags.
""",
        ),
        ("user", "What is the latest stable version of {software_name}?"),
    ]
)

VERSION_REGEX = r"(?s)<answer>.*?(\d+\.\d+(?:\.\d+)?(?:[-.][A-Za-z0-9]+)*).*?</answer>"

# Sanity check on the regex
assert (
    re.search(VERSION_REGEX, "<answer>3.12.1</answer>").group(  # type: ignore
        1
    )
    == "3.12.1"
)

assert (
    re.search(VERSION_REGEX, "<answer> 3.12.1 </answer>").group(  # type: ignore
        1
    )
    == "3.12.1"
)

assert (
    re.search(
        VERSION_REGEX,
        """<answer>
The latest stable version of pydantic is <version>2.3.3</version>.
</answer>""",
    ).group(1)  # type: ignore
    == "2.3.3"
)

assert (
    re.search(
        VERSION_REGEX,
        """</thinking>
<answer>
FastAPI version 0.110.0
</answer>""",
    ).group(1)  # type: ignore
    == "0.110.0"
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
    logger.info("Starting LLM version evaluation")

    # Load existing runs
    runs = load_runs_from_jsonl(RUNS_FILE)
    logger.info(f"Loaded {len(runs)} existing runs from {RUNS_FILE}")

    # Determine which (LLM, TechVersion) combos have not yet been evaluated
    pairs_to_run = [(llm, gt) for llm in LLMS for gt in GROUND_TRUTHS]
    missing = get_missing_runs(pairs_to_run, runs)

    if missing:
        logger.info(f"Executing {len(missing)} new runs...")
    else:
        logger.info("No new runs to execute.")

    # Execute runs for missing pairs
    for llm_config, ground_truth in tqdm(missing, desc="Evaluating LLMs"):
        logger.info(f"Running {llm_config.model} for {ground_truth.tech.name}...")
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
            logger.debug(f"Wrote run to {RUNS_FILE}")

    # Evaluate and print results
    logger.info("Evaluating final results...")
    evaluate_runs(runs)
    logger.info("Evaluation complete")


if __name__ == "__main__":
    main()
