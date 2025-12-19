from youtube_transcript_api import YouTubeTranscriptApi
from fastmcp import FastMCP

mcp = FastMCP("YouTube Transcript")

@mcp.tool
def get_youtube_transcript(video_id: str):
    """Gets the transcript for a given YouTube video ID.

    Args:
        video_id: The ID of the YouTube video.
    """
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id).to_raw_data()
        transcript = " ".join([item['text'] for item in transcript_list])
        return transcript
    except Exception as e:
        return f"Error getting transcript: {e}"

if __name__ == "__main__":
    mcp.run()
