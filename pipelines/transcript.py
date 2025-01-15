"""
Transcribe a video from a given URL.
Usage:
    python pipelines/transcript.py <video_url> [<output_dir>]
    <video_url>: The URL
    <output_dir>: The directory to write the transcript to. Default is the current directory.
Ouptut:
    A JSON file containing the transcript of the video.
    - url: The URL of the video.
    - title: The title of the video.
    - created_at: The timestamp when the transcript was created.
    - transcription: The transcript of the video.
    - transcription_chunks: The transcript chunks with timestamps.
"""

from langchain_community.callbacks import get_openai_callback
from langchain_openai import AzureChatOpenAI
from transformers import pipeline
import argparse
import dotenv
import json
import os
import re
import subprocess
import time

dotenv.load_dotenv()

def timer(func):
    def wrapper(*args, **kwargs):
        print("=" * 80)
        print(f"Running {func.__name__}")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Complete {func.__name__}, {end_time - start_time:.2f} sec")
        print("=" * 80)
        return result
    return wrapper

def parse_args():
    parser = argparse.ArgumentParser(description='Generate a transcript from a video link.')
    parser.add_argument('video_url', type=str, help='The URL of the video to transcribe')
    parser.add_argument('output_dir', type=str, nargs='?', help='The directory to write the transcript to', default='.')
    args = parser.parse_args()
    return args

@timer
def download_video(url, output_dir, output_file):
    """
    Downloads a video from the given URL and saves it to the specified output directory.
    Args:
        url (str): The URL of the video to download.
        output_dir (str): The directory where the downloaded video will be saved.
        output_file (str): The name of the downloaded video file.
    Returns:
        str: The full path to the downloaded video file.
    Raises:
        ValueError: If the video name and extension cannot be extracted from the download output.
    """
    # Ensure the output directory exists
    os.makedirs(os.path.expanduser(output_dir), exist_ok=True)
    
    # Construct the you-get command
    command = f"you-get -o {os.path.expanduser(output_dir)} -O {output_file} '{url}'"
    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # extract ext .mp4 or .webm. if contains multiple, take the last one
    exts = re.findall(r"\.(mp4|webm)", result.stderr + result.stdout)

    if not exts:
        raise ValueError("Cannot extract video extension from download output")
    
    return os.path.join(output_dir, f"{output_file}.{exts[-1]}")

@timer
def extract_audio(video_path):
    """
    Extract the audio from a video file.
    Save the audio to a file with the same name as the video but with a .wav extension.
    """
    # Ensure the video file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    
    # Construct the ffmpeg command
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    command = f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_path}"
    
    # Execute the command
    subprocess.run(command, shell=True)
    
    return audio_path

@timer
def run_whisper(audio_path):
    """
    Run the Whisper speech-to-text model on the given audio file.
    Args:
        audio_path (str): The path to the audio file to transcribe.
    Returns
        str: The transcript of the audio file.
    """
    pipe = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-small",
        chunk_length_s=30,
    )
    transcription_chunks = pipe(audio_path, batch_size=4, return_timestamps=True)["chunks"]
    # [{text: str, timestamp: (a, b)}] -> <a -> b> text ...
    transcription = "\n".join([t["text"] for t in transcription_chunks])
    return transcription, transcription_chunks

@timer
def run_refine(transcript):
    """
    Refine the transcript, fix problems based on the context.
    Args:
        transcript (str): The original transcript to refine.
    Returns:
        str: The refined transcript.
    """
    prompt = f"""
    <transcript>{transcript}</transcript>
    Above is a transcript of a video.
    Based on the above transcript, fix errors based on the context of transcript. Write the fixed transcript below, whithout any explanation.
    Transcription are in the format of <start_time -> end_time> text.
    Fix these errors:
    - Repeated words
    - Incorrect words
    - Missing words
    - Proper formatting
    Improve these:
    - Transcription may have errors, infer the correct words based on the context.
    Output in the same format as the input, but with the errors fixed."""
    model = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )
    with get_openai_callback() as cb:
        refined_transcript = model.invoke(prompt).content
    print(f"Total tokens: {cb.total_tokens}; Total cost: {cb.total_cost}")
    refined_transcript = re.search(r"<transcript>(.*?)</transcript>", refined_transcript, re.DOTALL).group(1)
    return refined_transcript

@timer
def extract_title(transcript):
    """
    Extract the title of the video from the transcript.
    Args:
        transcript (str): The transcript of the video.
    Returns:
        str: The title of the video.
    """
    prompt = f"""
    <transcript>{transcript}</transcript>
    Above is a transcript of a video.
    Based on the above transcript, extract the title of the video.
    - Use the language of the transcript. If transcript is in English, extract the title in English.
      If Chinese, extract the title in Chinese, so on and so forth.
    - Return plain text, without any formatting, spaces, line breaks, etc.
    - Title should be a single sentence, not a paragraph.
    - Clear and concise, to the point. Best describe the content of the video.
    """
    model = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment="gpt-4o-mini",
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0,
    )
    title = model.invoke(prompt).content
    return title

def transcript(video_url, output_dir):
    random_name = re.sub(r"[^a-zA-Z0-9]", "_", video_url)

    temp_file = []

    try:
        # Download the video
        video_path = download_video(video_url, output_dir, random_name)
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        temp_file.append(video_path)

        # Extract the audio from the video
        audio_path = extract_audio(video_path)
        temp_file.append(audio_path)

        # Perform speech-to-text on the audio
        transcription, transcription_chunks = run_whisper(audio_path)

        packed = {
            "url": video_url,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S %z'),
            "transcription": transcription,
            "transcription_chunks": transcription_chunks,
        }
        fn = os.path.join(output_dir, f"{video_name}.json")
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(packed, f, ensure_ascii=False, indent=4)
        temp_file.append(fn)
        
        # Extract title
        video_title = extract_title(transcription)

        packed = {
            "url": video_url,
            "title": video_title,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S %z'),
            "transcription": transcription,
            "transcription_chunks": transcription_chunks,
        }
        fn = os.path.join(output_dir, f"{video_name}_{video_title}.json")
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(packed, f, ensure_ascii=False, indent=4)

        # Refine the transcript
        refined_transcript = run_refine(transcription)

        packed = {
            "url": video_url,
            "title": video_title,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S %z'),
            "transcription": refined_transcript,
            "transcription_chunks": transcription_chunks,
        }
        fn = os.path.join(output_dir, f"{video_name}_{video_title}.json")
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(packed, f, ensure_ascii=False, indent=4)
    finally:
        for f in temp_file:
            if os.path.exists(f):
                os.remove(f)

def main():
    args = parse_args()
    video_url = args.video_url
    output_dir = os.path.expanduser(args.output_dir)
    transcript(video_url, output_dir)

if __name__ == "__main__":
    main()
