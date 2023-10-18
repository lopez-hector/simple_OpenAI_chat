import argparse

# use shpotify to cli control spotify
cli_docs = """
spotify play                       Resumes playback where Spotify last left off.
spotify play <song name>           Finds a song by name and plays it.
spotify play album <album name>    Finds an album by name and plays it.
spotify play artist <artist name>  Finds an artist by name and plays it.
spotify play list <playlist name>  Finds a playlist by name and plays it.
spotify play uri <uri>             Play songs from specific uri.

spotify next                       Skips to the next song in a playlist.
spotify prev                       Returns to the previous song in a playlist.
spotify replay                     Replays the current track from the beginning.
spotify pos <time>                 Jump to a specific time (in seconds) in the current song.
spotify pause                      Pauses (or resumes) Spotify playback.
spotify stop                       Stops playback.
spotify quit                       Stops playback and quits Spotify.

spotify vol up                     Increases the volume by 10%.
spotify vol down                   Decreases the volume by 10%.
spotify vol <amount>               Sets the volume to an amount between 0 and 100.
spotify vol [show]                 Shows the current volume.

spotify status                     Shows the play status, including the current song details.
spotify status artist              Shows the currently playing artist.
spotify status album               Shows the currently playing album.
spotify status track               Shows the currently playing track.

spotify share                      Displays the current song's Spotify URL and URI.
spotify share url                  Displays the current song's Spotify URL and copies it to the clipboard.
spotify share uri                  Displays the current song's Spotify URI and copies it to the clipboard.

spotify toggle shuffle             Toggles shuffle playback mode.
spotify toggle repeat              Toggles repeat playback mode.
"""

RECURRING_PROMPT = """
If i can return a valid CLI call to fullfill the request:

return JSON ONLY:
    {"cli_call": "CLI_CALL"}
    
If i need more info about what you want to listen to, i'd be happy to provide you with the information you need:

return:
    {"chat": "response to users questions"}
    
return JSON
"""

SPOTIFY_PROMPT = f"""
RETURN JSON
I am a helpful agent that considers your music requests. I understand that you may have specific or broad music requests. If you need help picking i will help you find music you like. I can also look up historical data to help you! Billboards data will be useful for this. I will prioritize answering your questions, showing you options, and then making a cli_call if we agree on the exact music to play.
 
I will do my best to distill your request into actionable CLI calls. 
I will always return JSON with either a 'chat' or 'cli_call' key. 

RETURN JSON
CLI_DOCUMENTATION:
{cli_docs}
RETURN JSON
{RECURRING_PROMPT}"""


def llm_dj(music_request: str):
    from cli_calls import CliLlmCalls

    spotify_cli_agent = CliLlmCalls(
        agent_name='Spotify',
        user_name='MusicRequest',
        orienting_system_message=SPOTIFY_PROMPT
    )
    spotify_cli_agent.chat(initial_message=music_request)


if __name__ == '__main__':
    # get user question
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-r',
                        "--request",
                        type=str,
                        help="User Request")

    args = parser.parse_args()

    llm_dj(music_request=args.request)
