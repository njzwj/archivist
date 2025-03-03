import subprocess
import json
import os

class VideoGetterService:

    def __init__(self):
        pass
    
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
