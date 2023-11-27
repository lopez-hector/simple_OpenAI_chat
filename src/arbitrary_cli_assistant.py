import argparse

# use shpotify to cli control spotify
cli_docs = """
If using a library place docs here
"""

# This is the response formatting prompt
RECURRING_PROMPT = """
If i can return a valid CLI call to fullfill the request:

return JSON ONLY:
    {"cli_call": "CLI_CALL"}

If i need more info about what you want to listen to, i'd be happy to provide you with the information you need:

return:
    {"chat": "response to users questions"}

return JSON
"""

# main prompt
CLI_PROMPT = f"""
I am a helpful agent that converses with you and responds with appropriate command line interface calls if appropriate.
The existing operating system is macOS.

I will do my best to distill your request into actionable CLI calls. I will do what I need to make sure the cli calls are valid.
This includes formatting, confirming that files or directories exists, and whatever else may be needed.

I will always return JSON with either a 'chat' or 'cli_call' key. 

RETURN JSON
{RECURRING_PROMPT}"""


def llm_cli_assistant(cli_request: str, debug=False):
    from generalchatassistant import GeneralChatAssistant

    cli_assistant = GeneralChatAssistant(
        agent_name='CommandLineAssistant',
        user_name='CLIRequest',
        orienting_system_message=CLI_PROMPT,
        return_json=True,
        debug=debug
    )
    cli_assistant.chat(initial_message=cli_request)


if __name__ == '__main__':
    # get user question
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-r',
                        "--request",
                        type=str,
                        help="User Request")

    args = parser.parse_args()

    llm_cli_assistant(cli_request=args.request)
