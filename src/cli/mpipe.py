from tqdm import tqdm
from typing import List
import argparse
import os

from ..core.item_model import ItemModel
from ..pipelines import orchestrator
from ..utils.config import get_config
from ..utils.decorators import timer, count_tokens

config = get_config()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run specific pipelines that output the results to the original file."
    )
    parser.add_argument(
        "pipeline",
        type=str,
        help="The pipeline to run",
        choices=orchestrator.list_pipelines(),
    )
    parser.add_argument(
        "args",
        type=str,
        help="The arguments to pass to the pipeline",
        nargs="*",
        default=[],
    )
    args = parser.parse_args()
    return args

def parse_arguments(args: List[str]) -> dict:
    return dict(arg.split("=", 1) for arg in args)

def run_pipeline_on(path: str, pipeline: str, **kwargs):
    item = ItemModel.from_file(path)
    results = orchestrator.process(pipeline, item.data, **kwargs)
    # compare results to item.data, if the same then do nothing
    if results != item.data:
        item.data = results
        item.save()

@timer()
@count_tokens()
def mpipe_wrapper():
    args = parse_args()
    kwargs = parse_arguments(args.args)

    path = config.power_llm_results_path

    json_files = [file for file in os.listdir(path) if file.endswith(".json")]
    for file in tqdm(json_files, desc="Processing files"):
        run_pipeline_on(os.path.join(path, file), args.pipeline, **kwargs)

def mpipe():
    mpipe_wrapper()
