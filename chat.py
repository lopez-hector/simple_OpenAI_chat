from typing import List

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessage,
    AIMessagePromptTemplate,
    AIMessage,
    HumanMessage,
)
import argparse
from utils import get_formatted_text
import functools
from colorama import Fore, Back, Style
import pyperclip


def execute_human_tasks(human_input: str, conversation: List[AIMessage]):
    if human_input.lower() in ['copy', 'copy to clipboard']:
        text_to_copy = conversation[-1].content
        pyperclip.copy(text_to_copy)
        print(f'{Fore.RED}\n\tCopied to clipboard!')
        print(f'Text Copied: {text_to_copy[:20]} ... {text_to_copy[-20:]}')
        return True
    else:
        return False


def main(model: str = 'gpt-3.5-turbo', system_message: str = None):
    LLM = ChatOpenAI(model_name=model, max_tokens=2000)

    if system_message is None:
        system_message = "I'm a helpful assistant. If the user has no further questions or the conversation has clearly ended I will expcitly return the phrase: ```Have a nice day!!!``` without any added text."

    # what should the model do with your input
    system_message_prompt = SystemMessage(
        content=system_message)
    conversation = [system_message_prompt]
    human_input = ''
    while human_input != 'quit':

        # get user input loop. User must provide `/end` to get answer
        # while loop allows user to hit return key but continue adding text in CLI
        human_input = grab_user_input()

        executed: bool = execute_human_tasks(human_input, conversation)
        if executed:
            continue

        # check for escape keywords (bypasses llm call)
        if human_input.lower() == 'quit':
            print('EXITING')
            break

        # convert human input to HumanMessage
        human_message_prompt = HumanMessage(content=human_input)
        conversation.append(human_message_prompt)

        output = llm_call(LLM, conversation)

        print('\n\t', get_formatted_text(output).replace('\n', '\n\t'))

        # LLM escape sequence (from prompt engineering)
        if output.lower().strip() == 'Have a nice day!!!'.lower():
            print('EXITING')
            break

        # update conversation history
        ai_message_prompt = AIMessage(content=output)
        conversation.append(ai_message_prompt)


def llm_call(LLM, conversation):
    chat_prompt = ChatPromptTemplate.from_messages(conversation)
    # run as a chain
    chain = LLMChain(llm=LLM, prompt=chat_prompt, )
    output = chain.run(input_language="English")
    return output


def grab_user_input() -> str:
    end_token = '//'  # /end

    grab_input = []
    while True:
        if not grab_input:
            grab_input.append(input(f'{Fore.LIGHTMAGENTA_EX}{Back.BLACK}User: '))
        else:
            grab_input.append(input(''))

        # check for exit keywords
        if grab_input[-1] == end_token:
            grab_input.pop()
            break
        elif grab_input[-1][-len(end_token):] == end_token:
            grab_input[-1] = grab_input[-1][:-len(end_token)]

            break
        elif grab_input[-1] == 'quit':
            grab_input = ['quit']
            break
    return ''.join(grab_input)


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

    acceptable_models = {'gpt-4', 'gpt-3.5-turbo'}

    # Call the main function and pass the model_name argument
    if args.model_name and args.model_name in acceptable_models:
        main(model=args.model_name, system_message=args.system_message)
    else:
        print('defaulting to chat-gpt (gpt-3.5-turbo)')
        main(model='gpt-3.5-turbo', system_message=args.system_message)
