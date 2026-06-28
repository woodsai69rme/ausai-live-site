from youtube_transcript_api import YouTubeTranscriptApi
import json

video_ids = ["ddQq04IVLZU"]

for vid in video_ids:
    try:
        # Try using the list_transcripts method which seems more robust in recent versions
        transcript_list = YouTubeTranscriptApi.list_transcripts(vid)
        transcript = transcript_list.find_transcript(['en', 'pt'])
        data = transcript.fetch()
        print(f"Success for {vid}: {len(data)} entries")
    except Exception as e:
        print(f"Error for {vid}: {str(e)}")
