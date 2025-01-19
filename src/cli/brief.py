from langchain_community.callbacks import get_openai_callback
import argparse
import dotenv
import os
import re
import time
from datetime import datetime, timedelta

from ..pipelines import summarize_one, format_markdown, load_json


dotenv.load_dotenv()

power_llm_results_path = os.path.expanduser(os.getenv('POWER_LLM_RESULTS_PATH'))

current_date = datetime.now().strftime('%Y-%m-%d')
default_briefing_path = os.path.join(power_llm_results_path, f'{current_date}-briefing.md')

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Complete {func.__name__}, {end_time - start_time:.2f} sec")
        return result
    return wrapper

def count_tokens(func):
    def wrapper(*args, **kwargs):
        with get_openai_callback() as cb:
            res = func(*args, **kwargs)
            print("=== OpenAI API Usage ===")
            print(f"Tokens used: {cb.total_tokens}")
            print(f"Total cost: ${cb.total_cost:.2f}")
            print("========================")
            return res
    return wrapper

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

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a briefing from the results directory.')
    parser.add_argument('-i', '--input_dir', type=str, help='The directory containing the JSON files', default=power_llm_results_path)
    parser.add_argument('-t', '--time', type=str, help='The time range to summarize', default='3 day')
    parser.add_argument('-o', '--output_file', type=str, help='The output file to write the briefing to', default=default_briefing_path)
    args = parser.parse_args()
    return args

def summarize_with_cache(d):
    cache_key = 'summarization'
    if cache_key in d:
        return d[cache_key]
    summarized = summarize_one(d)
    d[cache_key] = summarized
    return summarized

@timer
@count_tokens
def summarize_wrapper(time, input_dir, output_file):
    st = start_time(time)
    files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    data = [load_json(os.path.join(input_dir, f)) for f in files]
    data = [d for d in data if d['created_at'].replace(tzinfo=None) > st]
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
        lines.append(f'来源 [{d["title"]}]({d["source"]})')
        lines.append(f'获取时间: {d["created_at"].strftime("%Y-%m-%d %H:%M:%S")}')
        lines.append('\n' + summarized)
    
    formatted = format_markdown('\n'.join(lines))
    with open(output_file, 'w') as f:
        f.write(formatted)

def brief():
    args = parse_args()
    summarize_wrapper(args.time, args.input_dir, args.output_file)
