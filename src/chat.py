from cli_calls import CliLlmCalls
import argparse

DEFAULT_SYSTEM_MESSAGE = "I'm a helpful assistant. If the user has no further questions or the conversation has clearly ended I will expcitly return the phrase: ```Have a nice day!!!``` without any added text."


def main(model_name, system_message):

    chat_assistant = CliLlmCalls(
        agent_name='Assistant',
        orienting_system_message=system_message,
        model=model_name,
        temperature=1,
    )

    chat_assistant.chat()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-m',
                        "--model_name",
                        type=str,
                        help="Name of the model")
    parser.add_argument('-s',
                        "--system_message",
                        type=str,
                        help="Custom System Message for instantiating model")

    args = parser.parse_args()

    acceptable_models = {'gpt-4', 'gpt-3.5-turbo', 'gpt-3.5-turbo-1106', 'gpt-4-1106-preview'}

    if args.model_name is None:
        print('defaulting to chat-gpt (gpt-3.5-turbo-1106)')
        args.model_name = 'gpt-3.5-turbo-1106'

    if args.model_name not in acceptable_models:
        raise ValueError(f'Model {args.model_name} not allowed. Choose from: {acceptable_models}')

    # Call the main function and pass the model_name argument
    system_message = args.system_message if args.system_message else DEFAULT_SYSTEM_MESSAGE

    main(args.model_name, system_message)
