import json
from src.models import EvaluationRun, LLMConfig, TechVersionGroundTruth


def load_runs_from_jsonl(filepath: str) -> list[EvaluationRun]:
    """
    Loads evaluation runs from a JSON Lines file.

    :param filepath: Path to a .jsonl file containing runs data.
    :return: A list of EvaluationRun objects.

    Usage:
        runs = load_runs_from_jsonl("runs.jsonl")
    """
    runs = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                try:
                    run_data = json.loads(line)
                    run = EvaluationRun(**run_data)
                    runs.append(run)
                except Exception as e:
                    print(f"Error parsing run data: {e}\n line={line!r}")
    except FileNotFoundError:
        print(f"Runs file not found: {filepath}")
        return []
    return runs


def get_missing_runs(
    pairs: list[tuple[LLMConfig, TechVersionGroundTruth]],
    runs: list[EvaluationRun],
) -> list[tuple[LLMConfig, TechVersionGroundTruth]]:
    """
    Returns a list of (LLMConfig, TechVersionGroundTruth) pairs
    for which no run exists yet in 'runs'.

    :param pairs: Candidate list of (LLMConfig, TechVersionGroundTruth).
    :param runs: Existing runs that have already been executed.
    :return: Subset of 'pairs' that have not been run yet.
    """
    existing_keys = {(run.llm_config, run.ground_truth) for run in runs}
    missing = []
    for llm, gt in pairs:
        if (llm, gt) not in existing_keys:
            missing.append((llm, gt))
    return missing
