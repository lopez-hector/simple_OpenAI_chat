import subprocess

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessage,
    AIMessage,
    HumanMessage,
)
import argparse

from utils import llm_call, get_formatted_text, grab_user_input
from colorama import Fore

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

return JSON:
    {"cli_call": "CLI_CALL"}
    
If i need more info about what you want to listen to:

return JSON:
    {"chat": "chat"}
    
return JSON
"""

SPOTIFY_PROMPT = f"""
RETURN JSON
I am a helpful agent that considers your music requests. I understand that you may have specific or broad music requests. I will do my best to distill your request into actionable CLI calls. If you need help picking i will help you find music you like. I will always return JSON with either a 'chat' or 'cli_call' key. I can also look up historical data to help you! Billboards data will be useful for this.
RETURN JSON
CLI_DOCUMENTATION:
{cli_docs}
RETURN JSON
{RECURRING_PROMPT}"""


def process_llm_output(llm_output):
    """
    The LLM response could be a direct response to the user (chat) or a need to execute a call.
    Here we either continue the conversation or execute the desired call.

    :param llm_output: Dict[str, str]. Keys should be 'chat' or 'cli_call'
        direct output from the LLM in response to the conversation.
    :return:
        ai_message_prompt_: AI response to be shown to the user

    """
    # the LLM doesnt always output the right format when chatting, so we can catch that error here
    try:
        output_json = eval(llm_output)
    except:
        output_json = {'chat': llm_output}

    chatting_state: bool = False  # True if chatting, false if executing a command

    # if the LLM wants to chat, continue the conversation
    if 'chat' in output_json:
        # print('chat')
        # Show LLMs chat response
        print(get_formatted_text(output_json['chat']).replace('\n', '\n\t'))
        ai_message_prompt_ = AIMessage(content=output_json['chat'])

        chatting_state = True
    # if the LLM wants to run a cli call, then execute
    elif 'cli_call' in output_json:
        # define response here
        # print('cli_call')
        ai_executing_response = 'Here you go.'
        ai_message_prompt_ = AIMessage(content=ai_executing_response)
        print(f'{Fore.LIGHTCYAN_EX}{ai_executing_response}')

        # Execute comand
        # TODO: Error Handling
        subprocess.run(output_json['cli_call'].split(' '), )
    else:
        ai_executing_response = "Sorry I couldn't do that, please try again"
        ai_message_prompt_ = AIMessage(content=ai_executing_response)

    return ai_message_prompt_, chatting_state


def llm_dj(music_request: str):
    acceptable_models = {'gpt-4', 'gpt-3.5-turbo'}
    model = 'gpt-4'

    # setup LLM to handle request
    temperature = 1
    LLM = ChatOpenAI(model_name=model, max_tokens=2000, temperature=temperature)
    system_message = SPOTIFY_PROMPT
    system_message_prompt = SystemMessage(
        content=system_message)

    # get initial response
    # unlike the standard chat scenario, we already have a human input, so we process the input first, before going into
    # the chat loop.
    conversation = [system_message_prompt, HumanMessage(content=music_request)]

    output = llm_call(
        LLM=LLM,
        conversation=conversation
    )

    # update conversation history
    ai_message_prompt, chat = process_llm_output(llm_output=output)
    conversation.append(ai_message_prompt)

    # if the LLM continues to chat, we can then go into a chat loop.
    human_input = ''
    while human_input != 'quit' and chat:
        human_input = grab_user_input(User='MusicRequest: ')

        # check for escape keywords (bypasses llm call)
        if human_input.lower() == 'quit':
            print('Exiting Spotify Chat')
            break

        human_message = HumanMessage(content=human_input)
        conversation.append(human_message)

        # add system message to remind the model of its output format
        # TODO: Explore alternatives to this
        conversation.append(SystemMessage(content='Remember to output JSON format.'))

        output = llm_call(
            LLM=LLM,
            conversation=conversation
        )

        ai_message_prompt, chat = process_llm_output(llm_output=output)
        conversation.append(ai_message_prompt)


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
