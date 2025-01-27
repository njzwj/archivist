# LLM Pipeline

This project is designed to:

1. **Manage Consumed Content**: Initially, it handles videos from public platforms like Bilibili and YouTube. Future updates will expand to other types of information.
2. **Streamline and Process Data**: It offers flexible processing capabilities, including:
   - **Tagging**
   - **Summarizing**
   - **Generating valuable ideas and insights**
3. **Extensible Capabilities**: The system is built to be easily extended with simple mechanisms.

## Usage Instructions

1. **Install Conda**: Ensure Conda is installed on your system.
2. **Set Up Environment**: Create a new Conda environment and install the required packages.

This project utilizes Hugging Face's Whisper for transcription tasks.

### Environment Configuration

Place your `.env` file in your user directory: `~/.power-llm.env`, and fill in the necessary environment variables. By default, the environment path is `~/.power-llm.env`, but you can specify a different path by setting the `POWER_LLM_ENV_PATH` environment variable.

The output directory is also specified in this `.env` file.

### Fetching Video Transcripts

To obtain a transcript of any video, use the following command:

```bash
get 'https://www.youtube.com/...' [output-dir]
```

This command saves a JSON file named after the video title in the specified output directory. If `output-dir` is omitted, the file is saved in the default directory.

### Generating a Brief

*Note: This feature is slated for deprecation and is currently not recommended for use.*

## Future Enhancements

- ~~[] Add cookie support.~~ *Attempted but unsuccessful due to YouTube access restrictions via DC.*
- [] Develop a new tool, `mpipe` (short for map pipe), to handle all tagging, rewriting, summarizing, etc. This tool will process all saved files, modifying or adding keys based on existing data, and then save the changes back to disk. This functionality is akin to the map function in map-reduce but tailored for LLM pipelines.
- [] Create a display tool named `brief` to showcase all abstracted information saved. This could be a local web server that renders the data into a user-friendly website.

## References

- **You-Get**: An excellent tool for this application.
- **Hugging Face**: User-friendly and highly effective for our needs.
