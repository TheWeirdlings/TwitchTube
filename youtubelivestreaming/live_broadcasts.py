def get_live_broadcasts(youtube, broadcast_status="all"):
    list_broadcasts_request = youtube.liveBroadcasts().list(
        # broadcastStatus="all",
        broadcastType="persistent",
        part="snippet,id",
        maxResults=1,
        mine=True,
    )

    list_broadcasts_response = list_broadcasts_request.execute()
    casts = list_broadcasts_response.get("items", [])
    for cast in casts:
        if "liveChatId" in cast['snippet']:
            return cast['snippet']['liveChatId']
    # while list_broadcasts_request:
    #     list_broadcasts_response = list_broadcasts_request.execute()
    #     return list_broadcasts_response.get("items", [])
    #     for broadcast in list_broadcasts_response.get("items", []):
    #       print "%s (%s)" % (broadcast["snippet"]["title"], broadcast["id"])
    #
    #       list_broadcasts_request = youtube.liveBroadcasts().list_next(
    #         list_broadcasts_request, list_broadcasts_response)
