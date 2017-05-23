def get_live_streams_list(youtube, id):
    list_broadcasts_request = youtube.liveStreams().list(
        part="snippet,id",
        id=id,
        maxResults=1,
    )
    list_broadcasts_response = list_broadcasts_request.execute()
    casts = list_broadcasts_response.get("items", [])
    return casts;
