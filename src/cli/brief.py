from langchain_core.runnables import RunnableGenerator, RunnablePassthrough, RunnablePick
from operator import itemgetter
from langchain_community.callbacks import get_openai_callback
import argparse
import dotenv
import os
import re
import time
import datetime
import json

from ..utils.config import get_config
from ..utils.decorators import timer, count_tokens
from ..runnables.prompts import write_article, format_markdown
from ..runnables.tools import load_from_file

config = get_config()
default_output_file = os.path.join(config.power_llm_results_path, f"briefing_{datetime.datetime.now().strftime('%Y-%m-%d')}.md")

cache_key = 'briefing'

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a briefing from the results directory.')
    parser.add_argument('-i', '--input_dir', type=str, help='The directory containing the JSON files', default=config.power_llm_results_path)
    parser.add_argument('-t', '--time', type=str, help='The time range to summarize', default='3 day')
    parser.add_argument('-o', '--output_file', type=str, help='The output file to write the briefing to', default=default_output_file)
    args = parser.parse_args()
    return args

def start_time(t):
    time_map = {
        'day': lambda x: timedelta(days=x),
        'week': lambda x: timedelta(weeks=x),
        'month': lambda x: timedelta(days=30 * x)  # Approximate month as 30 days
    }

    match = re.match(r'(\d+)\s*(day|week|month)', t)
    if not match:
        raise ValueError(f"Invalid time format: {t}")

    value, unit = match.groups()
    value = int(value)
    ret = datetime.now() - time_map[unit](value)
    return ret.replace(tzinfo=None)

def test_start_time(start, data):
    return data["created_at"].replace(tzinfo=None) >= start_time(start)

def load_json_paths(input_dir):
    return [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.json')]

def summarize_with_cache(d, start_time, language):
    created_at = datetime.datetime.fromisoformat(d["created_at"])
    if not test_start_time(start_time, created_at):
        return None

    if cache_key not in d:
        summarized = write_article({**d, "language": language})
        d = {**d, cache_key: summarized}

    return d

@timer
@count_tokens
def summarize_wrapper(time, input_dir, output_file):
    st = start_time(time)
    files = load_json_paths(input_dir)
    data = [load_from_file(f) for f in files]
    data = [summarize_with_cache(d, st, "Chinese Simplified") for d in data]
    data = [d for d in data if d is not None]

    for d, fn in zip(data, files):
        with open(fn, 'w') as f:
            f.write(json.dumps(d, indent=4, ensure_ascii=False))

    data = sorted(data, key=lambda x: x['created_at'])

    lines = [
        '# 简报',
        f'从 {st.strftime("%Y-%m-%d")} 到 {datetime.now().strftime("%Y-%m-%d")} 的简报',
        f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'下述内容是从网页、视频等来源提取的信息，仅供参考。',
    ]
    for d in data:
        summarized = summarize_with_cache(d)
        lines.append('\n---\n')
        lines.append(f'## {d["title"]}')
        lines.append(f'来源 [{d["title"]}]({d["url"]})')
        lines.append(f'获取时间: {d["created_at"].strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append('\n' + summarized)
    
    formatted = format_markdown('\n'.join(lines))
    with open(output_file, 'w') as f:
        f.write(formatted)

def brief():
    args = parse_args()
    summarize_wrapper(args.time, args.input_dir, args.output_file)
