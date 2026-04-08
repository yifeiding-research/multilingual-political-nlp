from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import time

API_KEY = "REMOVED"
youtube = build("youtube", "v3", developerKey=API_KEY)

six_months_ago = (datetime.now() - timedelta(days=180)).isoformat() + 'Z'

top_20_channels = [
    {'channel_name': 'Communauté des Français du Luxembourg (CFL)', 'channel_id': 'UCDGrC8XEWomqWZGEu8oIjWQ'},
    {'channel_name': 'Alternativ Demokratesch Reformpartei', 'channel_id': 'UCtzfyfD-93Z4d_5LsViXsLg'},
    {'channel_name': 'SvenClementClips', 'channel_id': 'UCenzucUTX7W_jGOIEaI8eGQ'},
    {'channel_name': 'EU Debates | eudebates.tv', 'channel_id': 'UCkXWisas7nopnXQVgqMwodQ'},
    {'channel_name': 'euronews (en français)', 'channel_id': 'UCW2QcKZiU8aUGg4yxCIditg'},
    {'channel_name': 'Clara Moraru', 'channel_id': 'UCol-x2y5UkoZajHYcFyznZA'},
    {'channel_name': 'Zentrum fir politesch Bildung', 'channel_id': 'UC9Xk70I3Tt0Uq2UxRZxgMWA'},
    {'channel_name': 'Kiwimedia', 'channel_id': 'UCL94Pn2GtUz78pMuf9sGmVg'},
    {'channel_name': 'Reality Explained', 'channel_id': 'UC_Qcjmf7vL19BYW_bHYSfAg'},
    {'channel_name': 'Exploring The Benelux', 'channel_id': 'UCagIFAR9S2HiYuzRy8DMOxg'},
    {'channel_name': 'Ruche33', 'channel_id': 'UCirB1_Q1kvufIeLhIQOBpIg'},
    {'channel_name': 'Paperjam', 'channel_id': 'UCW2faOqcsCkHcnaQ71ZHrFw'},
    {'channel_name': 'Brend Kersai', 'channel_id': 'UCMqN5oBvbCFldxguAobdmaQ'},
    {'channel_name': 'euronews (deutsch)', 'channel_id': 'UCACdxU3VrJIJc7ujxtHWs1w'},
    {'channel_name': 'WELT Nachrichtensender', 'channel_id': 'UCZMsvbAhhRblVGXmEXW8TSA'},
    {'channel_name': 'phoenix', 'channel_id': 'UCwyiPnNlT8UABRmGmU0T9jg'},
    {'channel_name': 'Rosa-Luxemburg-Stiftung', 'channel_id': 'UClp4017ICvSPjIEBZLeEwaQ'},
    {'channel_name': 'Gaza Lens', 'channel_id': 'UCeFrhFHWnMH8AiqKtI_fHvQ'},
    {'channel_name': 'SD Classes', 'channel_id': 'UC7PRoMerF3581Fb6W4SpqcQ'},
    {'channel_name': 'Bibek Sah', 'channel_id': 'UCoxsRlxLTwd2lIUa98-P0eA'}
]

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
                    'country': 'Luxembourg',
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

country_videos = []

print("Collecting Luxembourg data (multilingual)...\n")

for idx, channel in enumerate(top_20_channels, 1):
    try:
        print(f"[{idx}/20] {channel['channel_name']}")
        videos = get_channel_videos(channel['channel_id'], channel['channel_name'], six_months_ago)
        print(f"  Collected {len(videos)} videos")
        country_videos.extend(videos)
        time.sleep(1)
    except Exception as e:
        print(f"  Error: {e}")
        break

df = pd.DataFrame(country_videos)
df.to_excel('political_influencers_Luxembourg_NEW.xlsx', index=False)

print(f"\nTotal: {len(country_videos)} videos")
print("Saved: political_influencers_Luxembourg_NEW.xlsx")