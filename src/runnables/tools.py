import os
import re
import subprocess
import time
import json

from ..core.models import get_hf_whisper_large_v3_turbo
from ..utils.config import load_cookies


def created_at(_):
    return time.strftime("%Y-%m-%d %H:%M:%S %z")


def extract_downloaded_file_path(output, output_dir):
    r = r"title:\s+(.+)\n"
    ext_r = r"\.(mp4|webm)"

    title = re.search(r, output)
    if title:
        title = title.group(1)
    else:
        title = None
        raise ValueError(f"Cannot extract video title from {output}")

    # find file name from output directory
    file_name = None
    for root, _, files in os.walk(output_dir):
        for file in files:
            if title in file:
                if re.search(ext_r, file):
                    file_name = os.path.join(root, file)
                else:
                    os.remove(os.path.join(root, file))
    if file_name:
        return file_name
    raise ValueError(f"Cannot find downloaded video file in {output_dir}")


def get_video(url, output_dir):
    """
    Downloads a video from the given URL and saves it to the specified output directory.
    Args:
        url (str): The URL of the video to download.
        output_dir (str): The directory where the downloaded video will be saved.
    Returns:
        str: The full path to the downloaded video file.
    Raises:
        ValueError: If the video file extension is not found in the command output.
    """

    cookies = None
    try:
        cookies = load_cookies()
    except FileNotFoundError:
        pass

    os.makedirs(output_dir, exist_ok=True)
    command = f"you-get -o {output_dir} '{url}'"
    if cookies:
        command += f" -c '{cookies}'"
    result = subprocess.run(command, shell=True, capture_output=True)
    stdout, stderr = result.stdout.decode(), result.stderr.decode()
    file_name = extract_downloaded_file_path(stdout + stderr, output_dir)
    return file_name


def extract_audio(video_path):
    """
    Extract the audio from a video file.
    Save the audio to a file with the same name as the video but with a .wav extension.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found")
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    if os.path.exists(audio_path):
        return audio_path
    command = (
        f"ffmpeg -i '{video_path}' -vn -acodec pcm_s16le -ar 44100 -ac 2 '{audio_path}'"
    )
    subprocess.run(
        command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return audio_path


def transcript(audio_path):
    """
    Transcribes the audio file at the given path using a pre-trained Whisper model.

    Args:
        audio_path (str): The file path to the audio file to be transcribed.

    Returns:
        str: The transcribed text from the audio file.
    """
    pipe = get_hf_whisper_large_v3_turbo()
    chunks = pipe(audio_path, batch_size=4, return_timestamps=True)["chunks"]
    transcript = "".join([chunk["text"] for chunk in chunks])
    return transcript


def extract_title_from_path(path):
    """
    Extract the title from a file path.
    Args:
        path (str): The path from which to extract the title.
    Returns:
        str: The extracted title.
    """
    file_name = os.path.basename(path)
    title, _ = os.path.splitext(file_name)
    return title


def clean_temp_files(inputs):
    """
    Clean up temporary files created during the process.
    Args:
        inputs (dict): The inputs to the process.
    """
    for key, value in inputs.items():
        if key.endswith("_path") and os.path.exists(value):
            os.remove(value)


def write_to_file(inputs):
    output_dir = inputs["output_dir"]
    file_name = os.path.join(output_dir, inputs["title"] + ".json")
    content = {k: v for k, v in inputs.items() if k != "output_dir"}
    with open(file_name, "w") as f:
        f.write(json.dumps(content, indent=4, ensure_ascii=False))
    return inputs


def load_from_file(file_path):
    with open(file_path, "r") as f:
        return json.load(f)
