from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import time
import os

API_KEY = "REMOVED"
youtube = build("youtube", "v3", developerKey=API_KEY)

countries_config = {
    "Hungary": {"query": "politika Magyarország", "language": "hu"}
}

six_months_ago = (datetime.now() - timedelta(days=180)).isoformat() + 'Z'

def find_top_channels(country_name, search_query, language):
    channel_stats = {}
    next_page_token = None
    
    for page in range(4):
        search_request = youtube.search().list(
            q=search_query,
            part="snippet",
            maxResults=50,
            type="video",
            pageToken=next_page_token,
            relevanceLanguage=language
        )
        search_response = search_request.execute()
        
        for item in search_response['items']:
            channel_id = item['snippet']['channelId']
            channel_name = item['snippet']['channelTitle']
            
            if channel_id not in channel_stats:
                channel_stats[channel_id] = {
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'video_count': 0
                }
            channel_stats[channel_id]['video_count'] += 1
        
        next_page_token = search_response.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(0.5)
    
    sorted_channels = sorted(channel_stats.values(), key=lambda x: x['video_count'], reverse=True)
    return sorted_channels[:20]

def get_channel_videos(channel_id, channel_name, published_after):
    all_videos = []
    next_page_token = None
    
    while True:
        search_request = youtube.search().list(
            channelId=channel_id,
            part="snippet",
            maxResults=50,
            type="video",
            publishedAfter=published_after,
            order="date",
            pageToken=next_page_token
        )
        search_response = search_request.execute()
        
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        if video_ids:
            videos_request = youtube.videos().list(
                part="snippet,statistics",
                id=','.join(video_ids)
            )
            videos_response = videos_request.execute()
            
            for item in videos_response['items']:
                video_info = {
                    'channel_name': channel_name,
                    'channel_id': channel_id,
                    'video_title': item['snippet']['title'],
                    'published_date': item['snippet']['publishedAt'][:10],
                    'view_count': int(item['statistics'].get('viewCount', 0)),
                    'like_count': int(item['statistics'].get('likeCount', 0)),
                    'comment_count': int(item['statistics'].get('commentCount', 0)),
                    'video_url': f"https://www.youtube.com/watch?v={item['id']}",
                    'channel_url': f"https://www.youtube.com/channel/{channel_id}"
                }
                all_videos.append(video_info)
        
        next_page_token = search_response.get('nextPageToken')
        if not next_page_token:
            break
        time.sleep(0.5)
    
    return all_videos

for country_name, config in countries_config.items():
    filename = f"political_influencers_{country_name}.xlsx"
    
    if os.path.exists(filename):
        print(f"{filename} exists, skipping")
        continue
    
    try:
        print(f"\nProcessing {country_name}...")
        top_channels = find_top_channels(country_name, config['query'], config['language'])
        print(f"Found {len(top_channels)} channels")
        
        country_videos = []
        
        for idx, channel in enumerate(top_channels, 1):
            print(f"[{idx}/20] {channel['channel_name']}")
            videos = get_channel_videos(channel['channel_id'], channel['channel_name'], six_months_ago)
            print(f"  Collected {len(videos)} videos")
            
            for video in videos:
                video['country'] = country_name
            
            country_videos.extend(videos)
            time.sleep(1)
        
        df = pd.DataFrame(country_videos)
        df.to_excel(filename, index=False, engine='openpyxl')
        
        print(f"\n{country_name}: {len(country_videos)} videos saved to {filename}")
        
    except Exception as e:
        print(f"\nError: {e}")
        break

print("\nDone!")