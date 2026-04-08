from googleapiclient.discovery import build

API_KEY = "REMOVED"  

youtube = build("youtube", "v3", developerKey=API_KEY)

request = youtube.search().list(
    q="politics",
    part="snippet",
    maxResults=1,
    type="video"
)

response = request.execute()

print(response)
print("API TEST START")
