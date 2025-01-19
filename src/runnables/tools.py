from langchain_core.prompts import PromptTemplate
import json
import os
import re
import subprocess
import datetime

from ..core.models import get_hf_whisper_large_v3_turbo, get_azure_chat_openai

def created_at():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %z')

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

    url = url.split('?')[0].strip('/\\').strip('/')

    os.makedirs(output_dir, exist_ok=True)
    command = f"you-get -o {output_dir} '{url}'"
    result = subprocess.run(command, shell=True, capture_output=True)
    stdout, stderr = result.stdout.decode(), result.stderr.decode()
    file_name = re.search(r"([^\s]+\.(mp4|webm))", stdout + stderr)
    if file_name:
        file_name = file_name.group(1)
    else:
        file_name = None
    exts = re.findall(r"\.(mp4|webm)", stdout + stderr)
    if not exts:
        raise ValueError(stderr)
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
    command = f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 44100 -ac 2 {audio_path}"
    subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

def clean_temp_files(inputs):
    """
    Clean up temporary files created during the process.
    Args:
        inputs (dict): The inputs to the process.
    """
    for key, value in inputs.items():
        if key.endswith("_path") and os.path.exists(value):
            os.remove(value)

refine_transcript = PromptTemplate.from_template(
    """
    Refine the following transcript:
    '''
    {transcript}
    '''
    Above is a transcript of a video downloaded from the internet by a model.
    Refine the transcript, fix errors caused by the model, and make any necessary edits.
    Possible errors include misheard words, incorrect punctuation, homophones, and other transcription errors.
    Write directly without any explanation or additional information.
    """
) | get_azure_chat_openai() | (lambda x: x.content)

extract_title = PromptTemplate.from_template(
    """
    '''
    {transcript}
    '''
    Above is a transcript of a video.
    Based on the above transcript, extract the title of the video.
    - Use the language of the transcript. If transcript is in English, extract the title in English.
      If Chinese, extract the title in Chinese, so on and so forth.
    - Return plain text, without any formatting, spaces, line breaks, etc.
    - Title should be a single sentence, not a paragraph.
    - Clear and concise, to the point. Best describe the content of the video.
    """
) | get_azure_chat_openai() | (lambda x: x.content)

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

extract_tags = (
    lambda inputs: { "input": json.dumps(inputs, ensure_ascii=False) }
) | PromptTemplate.from_template(
    """
    '''
    {input}
    '''
    Above is a piece of information scraped and processed from the internet.
    You act as a content creator and need to generate tags for this piece of information.
    - The tags should be relevant to the content.
    - The tags should be concise and informative.
    - The tags should be separated by commas.
    - Tags should in English.
    - Tags should be single words or short phrases.
    Write directly below this line, without any explanation. Because post processing splits the text by comma, avoid using commas in the tags.
    """
) | get_azure_chat_openai() | (lambda x: x.content) | (lambda x: [tag.strip() for tag in x.split(",")])