# LLM Pipeline

## Get

Get contents from a web page, including the video transcript.



## Transcript

Transcribe a video from a given URL.
Usage:
```
    python pipelines/transcript.py <video_url> [<output_dir>]
```
`<video_url>`: The URL
`<output_dir>`: The directory to write the transcript to. Default is the current directory.

Ouptut:

A JSON file containing the transcript of the video.

    - url: The URL of the video.
    - title: The title of the video.
    - created_at: The timestamp when the transcript was created.
    - transcription: The transcript of the video.
    - transcription_chunks: The transcript chunks with timestamps.

## Summarize

Auto extract summarize and briefing based on conditions.
Usage:
```
python pipelines/summarize.py -i <input_dir> -t <time> -o <output_file>
```
input_dir, default is ./results

time, like 1 day, 2 day, 1 week, 1 month. default is 3 day.

Output a briefing to output file sort by time.

## TODO

[] Add cookie.
