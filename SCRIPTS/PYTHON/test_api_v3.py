from youtube_transcript_api import YouTubeTranscriptApi
import json

video_id = "ddQq04IVLZU"

try:
    print(f"Instantiating YouTubeTranscriptApi()...")
    api = YouTubeTranscriptApi()
    
    print(f"Trying api.list('{video_id}')...")
    transcript_list = api.list(video_id)
    print("Success with api.list()")
    
    transcript = transcript_list.find_transcript(['en', 'pt'])
    data = transcript.fetch()
    print(f"Data fetched: {len(data)} entries")
    
except Exception as e:
    print(f"Error: {str(e)}")
    
    try:
        print(f"Trying api.fetch('{video_id}')...")
        data = api.fetch(video_id)
        print(f"Success with api.fetch(): {len(data)} entries")
    except Exception as e2:
        print(f"Error with api.fetch(): {str(e2)}")
