def insert_message(youtube, live_chat_id, message):
    list_streams_request = youtube.liveChatMessages().insert(
        part="snippet",
        body=dict(
          snippet=dict(
            liveChatId=live_chat_id,
            type="textMessageEvent",
            textMessageDetails=dict(
              messageText=message
            )
          ),
        )
    ).execute()

    return list_streams_request

def list_messages(youtube, live_chat_id, pageToken=None):
    if (pageToken):
        list_broadcasts_request = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="id,snippet,authorDetails",
            pageToken=pageToken,
        )
    else:
        list_broadcasts_request = youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part="id,snippet,authorDetails",
        )

    while list_broadcasts_request:
        list_broadcasts_response = list_broadcasts_request.execute()
        return list_broadcasts_response
        # list_broadcasts_request = youtube.liveBroadcasts().list_next(
        #   list_broadcasts_request, list_broadcasts_response)
