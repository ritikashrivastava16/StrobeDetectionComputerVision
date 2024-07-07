# import slack
from slack_sdk import WebClient

from  dotenv import load_dotenv
import os
from slackeventsapi import SlackEventAdapter
# from flask import Flask,, Response, jsonify
import pprint
import requests
from strob_fix import *
import json
load_dotenv()


client = WebClient(token=os.environ['SLACK_TOKEN'])
slack_events_adapter = SlackEventAdapter(os.environ['SLACK_SIGNING_SECRET'],"/slack/events")

BOT_ID = client.api_call("auth.test")['user_id']

def process_video(video_url, video_id,params):
    # Download the video
    headers = {
                "Authorization": f"Bearer {os.environ['SLACK_TOKEN']}"
            }
    with requests.get(video_url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(f"videos/{video_id}.mp4", 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                
                f.write(chunk)
    inputFile = f"videos/{video_id}.mp4"
    outputFile = f"videos/{video_id}_fixed.mp4"
    threshold = params.get('threshold', 15)
    frame_skip = params.get('frame_skip', 1)
    start_stream(inputFile, outputFile,threshold, frame_skip)
    # os.remove(inputFile)
    return outputFile


def upload_video(video_paths, channel_id):
    """
    Upload the video file to the specified Slack channel.
    """
    file_uploads = []
    for path, name in video_paths:
        file_uploads.append(
            {
                "file": path,
                'title':name
            }
        )
    response = client.files_upload_v2(
        file_uploads=file_uploads,
        channel=channel_id,
        initial_comment="Alert! The above shared media contains photosensitive contents. Please refer the media shared here which is accessible to all",
    )
    pprint.pprint(response.get('files'))
    # for path, name in video_paths:   
        # os.remove(path)

@slack_events_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    # pprint.pprint(event)
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text','')
    print('*'*30)
    print(f'bot id:{BOT_ID},      user_id: {user_id}')
    print('*'*30)
    print(text)
    params = {}
    if '{threshold:' in text:
        params = json.loads(text) 
    if user_id!=BOT_ID:
        if 'files' in event:
            
            files = event["files"]
            video_list = []
            for file in files:
                pprint.pprint(file)
                if 'video' in file['mimetype'] or 'gif' in file['mimetype']:
                    video_url = file["url_private"]
                    video_id = file['id']
                    name = file['name']
                    video_list.append((process_video(video_url, video_id,params),name,))
            
            upload_video(video_list, channel_id)
            print('#'*30)


slack_events_adapter.start(port=3000,debug=True)
