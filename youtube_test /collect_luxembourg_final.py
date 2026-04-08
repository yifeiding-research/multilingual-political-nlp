from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import time

API_KEY = "REMOVED"
youtube = build("youtube", "v3", developerKey=API_KEY)

six_months_ago = (datetime.now() - timedelta(days=180)).isoformat() + 'Z'

luxembourg_channels = [
    {'name': 'Alternativ Demokratesch Reformpartei', 'id': 'UCtzfyfD-93Z4d_5LsViXsLg'},
    {'name': 'CSV - Chrëschtlech-Sozial Vollekspartei', 'id': 'UC7gdxu4HZ-lZmCwS2YgWw8Q'},
    {'name': 'Zesummen Progressiv', 'id': 'UClyJuDl6EMX5xHtx51gvCpw'},
    {'name': 'SvenClementClips', 'id': 'UCenzucUTX7W_jGOIEaI8eGQ'},
    {'name': 'Demokratesch Partei', 'id': 'UCN-m2EQN1XCJL6gbojvnEhQ'},
    {'name': 'LSAP', 'id': 'UCJviJrXL7jP1HLEbpZgFcgg'},
    {'name': 'Gouvernement LU', 'id': 'UCVZIMejammns_AsigHxxfFw'},
    {'name': 'Roude Fuedem', 'id': 'UCNt74KwUnzON9qRh5vLtu0Q'},
    {'name': 'Paperjam', 'id': 'UCW2faOqcsCkHcnaQ71ZHrFw'},
    {'name': 'Kloer & Däitlech', 'id': 'UC484P4bSa5Z2AlugzMUuXNg'},
    {'name': 'Nei Luxembourg', 'id': 'UCEawrf2r0QIDtGxACOcY8Xw'},
    {'name': 'Communauté des Français du Luxembourg (CFL)', 'id': 'UCDGrC8XEWomqWZGEu8oIjWQ'},
    {'name': 'Tageblatt Lëtzebuerg', 'id': 'UC5E-lqm0hYixrY61GAjXIdw'},
    {'name': 'Luxemburger Wort', 'id': 'UCh3MNRzicd8Yb_EX3Ml2JNA'},
    {'name': 'déi gréng', 'id': 'UCJJfKmTvh4fronvBocXVp1g'},
    {'name': '360Crossmedia', 'id': 'UCnAsAkwFWnBYWS0T-9eU73g'},
    {'name': 'Exploring The Benelux', 'id': 'UCagIFAR9S2HiYuzRy8DMOxg'},
    {'name': 'Chokitable Media', 'id': 'UCaEmXLrr0sNxwoJRTO34SRA'},
    {'name': 'Hubert Hollerich', 'id': 'UC4Feyq1eFZ6qABZxXJXJxrg'},
    {'name': 'AmChamLux', 'id': 'UC2DoxQMFD-pQzFOPTiMkXmw'}
]

def get_channel_videos(channel_id, channel_name, published_after):
    all_videos = []
    next_page_token = None
    
    while True:
        try:
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
        except Exception as e:
            print(f"    Error: {e}")
            break
    
    return all_videos

all_videos = []

print("Collecting Luxembourg political influencers...\n")

for idx, channel in enumerate(luxembourg_channels, 1):
    print(f"[{idx}/20] {channel['name']}")
    videos = get_channel_videos(channel['id'], channel['name'], six_months_ago)
    print(f"  Collected {len(videos)} videos")
    all_videos.extend(videos)
    time.sleep(1)

df = pd.DataFrame(all_videos)
df.to_excel('political_influencers_Luxembourg_FINAL.xlsx', index=False)

print(f"\nTotal: {len(all_videos)} videos")
print("Saved: political_influencers_Luxembourg_FINAL.xlsx")