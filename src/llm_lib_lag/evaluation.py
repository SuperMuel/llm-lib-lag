import logging
from typing import Sequence
from packaging.version import parse
from .models import EvaluationRun
import statistics  # Import the statistics module

logger = logging.getLogger(__name__)


def evaluate_runs(runs: Sequence[EvaluationRun]) -> None:
    """
    Takes a list of EvaluationRun objects and compares parsed versions
    to the ground truths. Logs per-LLM, per-software, and overall metrics.

    :param runs: A list of EvaluationRun objects with ground_truth + LLM outputs.
    """
    if not runs:
        logger.warning("No evaluation runs provided.")
        return

    # First, group runs by (software, provider, model) and keep only the latest
    latest_runs: dict[tuple[str, str, str], EvaluationRun] = {}
    for run in runs:
        key = (
            run.ground_truth.tech.name,
            run.llm_config.provider,
            run.llm_config.model,
        )
        if key not in latest_runs or run.timestamp > latest_runs[key].timestamp:
            latest_runs[key] = run

    filtered_runs = list(latest_runs.values())
    total_runs = len(filtered_runs)

    # Possibly some runs were duplicates
    if len(runs) != total_runs:
        logger.info(
            f"Filtered out {len(runs) - total_runs} older/duplicate runs, "
            "keeping only the latest run for each technology/LLM combination."
        )

    exact_matches = 0
    major_matches = 0
    minor_matches = 0
    total_execution_time = 0.0

    by_software: dict[str, list[EvaluationRun]] = {}
    by_llm: dict[str, list[EvaluationRun]] = {}

    for run in filtered_runs:
        name = run.ground_truth.tech.name
        llm_key = f"{run.llm_config.provider}/{run.llm_config.model}"

        # Group by software name
        by_software.setdefault(name, []).append(run)

        # Group by LLM
        by_llm.setdefault(llm_key, []).append(run)

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
                logger.error(
                    f"Error parsing version for {name} ({llm_key}): {str(e)}",
                    exc_info=True,
                )

    # Overall results
    logger.info("-" * 50)
    logger.info("Overall Evaluation Results:")
    logger.info(f"Total Runs Evaluated: {total_runs}")
    logger.info(f"Exact Matches: {exact_matches} ({exact_matches / total_runs:.2%})")
    logger.info(
        f"Major Version Matches: {major_matches} ({major_matches / total_runs:.2%})"
    )
    logger.info(
        f"Minor Version Matches: {minor_matches} ({minor_matches / total_runs:.2%})"
    )
    logger.info(
        f"Average Execution Time: {total_execution_time / total_runs:.2f} seconds"
    )
    logger.info("-" * 50)

    # Breakdown by software
    logger.info("\nResults by Tech:")
    for name, software_runs in by_software.items():
        logger.info(f"\n  {name}:")
        software_total = len(software_runs)
        software_exact = 0
        software_major = 0
        software_minor = 0
        software_lags: list[float] = []  # List to store lag_days for this software

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
                    if run.lag_days is not None:  # Check if lag_days is available
                        software_lags.append(run.lag_days)
                except Exception as e:
                    logger.error(
                        f"Error parsing version for {name} "
                        f"({run.llm_config.provider}/{run.llm_config.model}): {str(e)}",
                        exc_info=True,
                    )

        logger.info(f"    Total Runs: {software_total}")
        logger.info(
            f"    Exact Matches: {software_exact} "
            f"({software_exact / software_total:.2%})"
        )
        logger.info(
            f"    Major Matches: {software_major} "
            f"({software_major / software_total:.2%})"
        )
        logger.info(
            f"    Minor Matches: {software_minor} "
            f"({software_minor / software_total:.2%})"
        )
        if software_lags:
            logger.info(f"    Average Lag (days): {statistics.mean(software_lags):.2f}")
            logger.info(
                f"    Median Lag (days): {statistics.median(software_lags):.2f}"
            )
            logger.info(f"    Max Lag (days): {max(software_lags)}")
        else:
            logger.info("    Lag data not available for this software.")

    # Breakdown by LLM
    logger.info("\nResults by LLM:")
    for llm_key, llm_runs in by_llm.items():
        logger.info(f"\n  {llm_key}:")
        llm_total = len(llm_runs)
        llm_exact = 0
        llm_major = 0
        llm_minor = 0
        llm_total_time = 0.0
        llm_lags: list[float] = []  # List to store lag_days for this LLM

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
                    if run.lag_days is not None:
                        llm_lags.append(run.lag_days)
                except Exception as e:
                    logger.error(
                        f"Error parsing version for {run.ground_truth.tech.name} "
                        f"({run.llm_config.provider}/{run.llm_config.model}): {str(e)}",
                        exc_info=True,
                    )

        logger.info(f"    Total Runs: {llm_total}")
        logger.info(f"    Exact Matches: {llm_exact} ({llm_exact / llm_total:.2%})")
        logger.info(f"    Major Matches: {llm_major} ({llm_major / llm_total:.2%})")
        logger.info(f"    Minor Matches: {llm_minor} ({llm_minor / llm_total:.2%})")
        logger.info(
            f"    Average Execution Time: {llm_total_time / llm_total:.2f} seconds"
        )
        if llm_lags:
            logger.info(f"    Average Lag (days): {statistics.mean(llm_lags):.2f}")
            logger.info(f"    Median Lag (days): {statistics.median(llm_lags):.2f}")
            logger.info(f"    Max Lag (days): {max(llm_lags)}")
        else:
            logger.info("    Lag data not available for this LLM.")
