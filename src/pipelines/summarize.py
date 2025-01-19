"""
Auto extract summarize and briefing based on conditions.
Usage:
```
python pipelines/summarize.py -i <input_dir> -t <time> -o <output_file>
```
input_dir, default is ./results
time, like 1 day, 2 day, 1 week, 1 month. default is 3 day.

Output a briefing to output file sort by time.
"""

from langchain_community.callbacks import get_openai_callback
import argparse
import dotenv
import datetime
import re
import time
import json
import os
from langchain_openai import AzureChatOpenAI

dotenv.load_dotenv()

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a briefing from the results directory.')
    parser.add_argument('-i', '--input_dir', type=str, help='The directory containing the JSON files', default='./results')
    parser.add_argument('-t', '--time', type=str, help='The time range to summarize', default='3 day')
    parser.add_argument('-o', '--output_file', type=str, help='The output file to write the briefing to', default='briefing.md')
    args = parser.parse_args()
    return args

def start_time(t):
    time_map = {
        'day': lambda x: datetime.timedelta(days=x),
        'week': lambda x: datetime.timedelta(weeks=x),
        'month': lambda x: datetime.timedelta(days=30 * x)  # Approximate month as 30 days
    }

    match = re.match(r'(\d+)\s*(day|week|month)', t)
    if not match:
        raise ValueError(f"Invalid time format: {t}")

    value, unit = match.groups()
    value = int(value)
    return datetime.datetime.now() - time_map[unit](value)

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

def load_json(file_path):
    valid_title_fields = ['title', 'name', 'subject', 'topic']
    valid_content_fields = ['content', 'transcription']
    valid_created_at_fields = ['created_at', 'date', 'timestamp']
    valid_source_fields = ['source', 'url']
    with open(file_path, 'r') as f:
        obj = json.load(f)
    title = next((obj[field] for field in valid_title_fields if field in obj), None)
    content = next((obj[field] for field in valid_content_fields if field in obj), None)
    created_at = next((obj[field] for field in valid_created_at_fields if field in obj), None)
    source = next((obj[field] for field in valid_source_fields if field in obj), None)

    if not title or not content:
        raise ValueError(f"Invalid JSON file: {file_path}")

    created_at = datetime.datetime.fromisoformat(created_at) if created_at else None
    return dict(title=title, content=content, created_at=created_at, source=source)

def load_jsons_from_dir(dir):
    success_count = 0
    failure_count = 0
    for file in os.listdir(dir):
        if file.endswith('.json'):
            try:
                yield load_json(os.path.join(dir, file))
                success_count += 1
            except ValueError as e:
                print(f"Failed to load {file}: {e}")
                failure_count += 1
    print(f"Successfully loaded {success_count} JSON files.")
    print(f"Failed to load {failure_count} JSON files.")

def summarize_one(data):
    prompt = f"""
    <content>{data['content']}</content>
    Above is a content from internet. Rewrite it as a professional article (like The Economist article). Here are the key requirements:
    - Keep the main idea and key points.
    - Into well organized article, informative and engaging.
    - Well structured and developed.
    - In the size of an average blog post.
    - Papagraphs should be informative, not too scattered.
    - Reorganize if needed, better order, flow and coherence.
    - Write using Chinese. For names, terms you cannot infer, keep them in the original language.
    Format requirements:
    - Summarize keypoints briefly in the beginning, in lists and bullet points.
    - Rewrite the main content in paragraphs.
    - Use markdown.
    - Avoid using too many headings, lists, and bullet points.
    Example:
    - 要点1
      - 要点1.1
      ...
    ...
    
    正文内容

    Output directly below this line, without any explanation.
    """
    model = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )
    results = model.invoke(prompt)
    summary = results.content
    return summary

def format_markdown(md):
    prompt = f"""
    <content>{md}</content>
    Above is a markdown content. Format it to a more readable markdown content. Here are the key requirements:
    - Keep the original content.
    - Use h2 as each section title.
    - Use h1 as the title of the whole article.
    - Unless necessary, avoid using h3 and h4.
    - Make each section format aligned.
    Output directly below this line, without any explanation and xml tags."""
    model = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )
    results = model.invoke(prompt)
    formatted = results.content
    return formatted

def summarize(t, input_dir, output_file):
    start = start_time(t)
    print(f"Summarizing results from {start} to {datetime.datetime.now()}")

    data = sorted(load_jsons_from_dir(input_dir), key=lambda x: x['created_at'], reverse=True)
    data = [x for x in data if x['created_at'].replace(tzinfo=None) > start.replace(tzinfo=None)]

    lines = [
        "# 简报",
        "",
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} 生成",
    ]
    
    for item in data:
        summarized = summarize_one(item)

        lines.append(f"\n## {item['title']}")
        lines.append(f"\nSource: [{item['title']}]({item['source']})")
        created_at = item['created_at'].strftime("%Y-%m-%d %H:%M:%S") if item['created_at'] else None
        lines.append(f"\nCreated at: {created_at}")

        lines.append("\n" + summarized)
    
    with open(output_file, 'w') as f:
        f.write("\n".join(lines))

@timer
@count_tokens
def main():
    args = parse_args()
    summarize(args.time, args.input_dir, args.output_file)

if __name__ == "__main__":
    main()
