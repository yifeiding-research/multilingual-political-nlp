from googleapiclient.discovery import build
import pandas as pd
import time

API_KEY = "REMOVED"
youtube = build("youtube", "v3", developerKey=API_KEY)

search_queries = [
    "Luxembourg election",
    "Luxembourg government",
    "Lëtzebuerg Regierung",
    "politique luxembourgeoise",
    "CSV Luxembourg",
    "DP Luxembourg",
    "LSAP Luxembourg",
    "Déi Gréng Luxembourg",
    "Piratepartei Luxembourg",
    "Xavier Bettel",
    "Luc Frieden"
]

all_channels = {}

for query in search_queries:
    print(f"Searching: {query}")
    
    search_request = youtube.search().list(
        q=query,
        part="snippet",
        maxResults=50,
        type="video"
    )
    search_response = search_request.execute()
    
    for item in search_response['items']:
        channel_id = item['snippet']['channelId']
        channel_name = item['snippet']['channelTitle']
        
        if channel_id not in all_channels:
            all_channels[channel_id] = {
                'channel_name': channel_name,
                'channel_id': channel_id,
                'video_count': 0
            }
        all_channels[channel_id]['video_count'] += 1
    
    time.sleep(1)

sorted_channels = sorted(all_channels.values(), key=lambda x: x['video_count'], reverse=True)[:30]

print(f"\n{'='*70}")
print("TOP 30 CHANNELS")
print('='*70)
for idx, ch in enumerate(sorted_channels, 1):
    print(f"{idx}. {ch['channel_name']} ({ch['video_count']} appearances)")

with open('luxembourg_channels_extended.txt', 'w', encoding='utf-8') as f:
    for idx, ch in enumerate(sorted_channels, 1):
        f.write(f"{idx}. {ch['channel_name']} - {ch['channel_id']} ({ch['video_count']} appearances)\n")

print("\nSaved: luxembourg_channels_extended.txt")