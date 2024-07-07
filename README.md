# flickr_fix

### To detect and process strobing intervals in real-time using Flickr Fix, follow these steps:

1. Ensure you have Python and OpenCV installed on your system.
2. Clone or download the repository containing the code.
3. Navigate to the directory containing the code in your terminal or command prompt.
4. Run the following command to execute the code:
```
usage: real_time_stobbing_fix.py [-h] [--inputFile INPUTFILE] [--threshold THRESHOLD] [--frame_skip FRAME_SKIP] [--gap_threshold GAP_THRESHOLD] [--consecutive_strobe_threshold CONSECUTIVE_STROBE_THRESHOLD]

Mitigates strobbing effects in video

optional arguments:
  -h, --help            show this help message and exit
  --inputFile INPUTFILE
                        path of the given video file
  --threshold THRESHOLD (default = 25)
                        threshold for strobbing effect
  --frame_skip FRAME_SKIP (default = 1)
                        frames to skip in video
  --gap_threshold GAP_THRESHOLD (default = 0.7)
                        gap between strobbing frames
  --consecutive_strobe_threshold CONSECUTIVE_STROBE_THRESHOLD (default = 5)
                        strobbing frame window size
```



This command will process the input video, detect strobing effects, process frames to mitigate any potential harm and display the output video in real-time.

### To run slack bot
1. Create an app in [slack](https://api.slack.com/) and use OAuth token an signing secret for the slack bot by storing these values in environment variable.Make sure to give bot the permissin to read chats and files. ![Screenshot 2024-04-28 at 10 37 31 PM](https://media.github.iu.edu/user/20663/files/1e0aaac3-e862-41af-8dd4-e5ceadfd2edf)
![Screenshot 2024-04-28 at 10 37 13 PM](https://media.github.iu.edu/user/20663/files/2cb5b1ee-773e-4d07-be65-b6b8e506a03c)

2. Use [ngrok](https://ngrok.com/) to connect your localhost server to internet for webhook. Use the command `ngrok http 3000` to start the connection
3. Copy the link generated and past it in event subsriptions tap in slack api website adding slack/events as postfix. ![Screenshot 2024-04-28 at 10 38 56 PM](https://media.github.iu.edu/user/20663/files/6647878b-47de-43a7-bef8-0ed1b615ffdc)
4.  Start the server by running `python slack_bot.py `
