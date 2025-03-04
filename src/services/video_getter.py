import logging
import subprocess
import json
import os

class VideoGetterService:

    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def extract_title(self, out: str):
        if out == "":
            return None
        try:
            json_data = json.loads(out)
        except json.JSONDecodeError:
            return None
        return json_data["title"]

    def download_video(self, url: str, output_dir: str):
        # dry run to get title
        command = f"you-get '{url}' --json"
        result = subprocess.run(command, shell=True, capture_output=True)
        title = self.extract_title(result.stdout)
        if title is None:
            return None
        
        # download video
        command = f"you-get -o '{output_dir}' --no-caption '{url}'"
        result = subprocess.run(command, shell=True, capture_output=True)

        # scan for video file
        for file in os.listdir(output_dir):
            if file.startswith(title):
                return os.path.join(output_dir, file)
        return None
    
    def installed_ffmpeg(self):
        command = "ffmpeg -version"
        result = subprocess.run(command, shell=True, capture_output=True)
        return result.returncode == 0
    
    def extract_audio(self, video_path: str, output_dir: str):
        if not self.installed_ffmpeg():
            raise Exception("ffmpeg not installed, please install ffmpeg first.")

        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = os.path.join(output_dir, filename + ".aac")
        command = f"ffmpeg -i '{video_path}' -vn -acodec copy '{output_filename}'"
        result = subprocess.run(command, shell=True, capture_output=True)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to extract audio from video {video_path}.")

        return output_filename
