import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def reverse_playlist(youtube, orig_playlist_id):
    # Step 1: Create a new playlist with the opposite order
    orig_playlist_response = (
        youtube.playlists().list(part="snippet", id=orig_playlist_id).execute()
    )
    orig_playlist_title = orig_playlist_response["items"][0]["snippet"]["title"]
    new_playlist_title = f"{orig_playlist_title} (reversed)"
    new_playlist_description = "A reversed playlist"
    new_playlist_response = (
        youtube.playlists()
        .insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": new_playlist_title,
                    "description": new_playlist_description,
                },
                "status": {"privacyStatus": "private"},
            },
        )
        .execute()
    )
    new_playlist_id = new_playlist_response["id"]

    # Step 2: Get all the videos from the original playlist
    videos = []
    next_page_token = None
    while True:
        playlist_items_response = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=orig_playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            )
            .execute()
        )

        for item in playlist_items_response["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            videos.append(video_id)

        next_page_token = playlist_items_response.get("nextPageToken")
        if not next_page_token:
            break

    # Step 3: Add the videos to the new playlist in reverse order
    for video_id in reversed(videos):
        try:
            print(video_id)  # Add this line to print the video ID
            youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": new_playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id},
                    }
                },
            ).execute()
        except:
            print(f"Error occured with the video {video_id}")

    print(
        "New playlist created with the opposite order: https://www.youtube.com/playlist?list="
        + new_playlist_id
    )


# Set up the YouTube API client
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", scopes
)
credentials = flow.run_local_server(port=0)
youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

# Call the reverse_playlist function with a playlist ID
playlist_id = input("Enter the YouTube playlist ID: ")
reverse_playlist(youtube, playlist_id)
