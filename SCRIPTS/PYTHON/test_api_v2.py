from youtube_transcript_api import YouTubeTranscriptApi
import json

video_ids = ["ddQq04IVLZU"]

for vid in video_ids:
    try:
        # Based on dir() output, let's try the 'list' and 'fetch' methods
        # It's likely that 'list' returns a TranscriptList and 'fetch' is the static equivalent of get_transcript
        
        print(f"Trying list({vid})...")
        transcript_list = YouTubeTranscriptApi.list(vid)
        print("Success with list()")
        
        transcript = transcript_list.find_transcript(['en', 'pt'])
        data = transcript.fetch()
        print(f"Data fetched: {len(data)} entries")
        
    except Exception as e:
        print(f"Error for {vid}: {str(e)}")
        
        print(f"Trying fetch([{vid}])...")
        try:
            data = YouTubeTranscriptApi.fetch([vid])
            print(f"Success with fetch(): {len(data)} entries")
        except Exception as e2:
            print(f"Error with fetch(): {str(e2)}")
