import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def reverse_playlist(youtube, playlist_id):
    # Retrieve the videos in the original playlist
    playlist_items = []
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()
        playlist_items += playlist_response["items"]
        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break
    
    # Create a new playlist with the opposite order
    new_playlist_request = youtube.playlists().insert(
        part="snippet",
        body={
            "snippet": {
                "title": "Reversed " + playlist_response["snippet"]["title"],
                "description": playlist_response["snippet"]["description"]
            }
        }
    )
    new_playlist_response = new_playlist_request.execute()
    new_playlist_id = new_playlist_response["id"]
    
    for item in reversed(playlist_items):
        video_id = item["snippet"]["resourceId"]["videoId"]
        add_video_request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": new_playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        add_video_request.execute()

    print("New playlist created with the opposite order: https://www.youtube.com/playlist?list=" + new_playlist_id)


# Set up the YouTube API client
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", scopes)
credentials = flow.run_local_server(port=0)
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Call the reverse_playlist function with a playlist ID
playlist_id = input("Enter the YouTube playlist ID: ")
reverse_playlist(youtube, playlist_id)
