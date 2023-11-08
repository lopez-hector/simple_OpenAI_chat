from typing import List

import pyperclip
from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from colorama import Fore, Back, Style

from spotify import llm_dj

def get_code_formatted(code, language):
    try:
        lexer = get_lexer_by_name(language)
    except:
        lexer = PythonLexer()

    formatter = TerminalFormatter(style=get_style_by_name('xcode'))
    return highlight(code, lexer, formatter)


def get_formatted_text(input):
    """
    Converts input to formatted code and text.
    :param input:
    :return:
    """

    code_marker = '```'
    split_text = input.split(code_marker)

    # Every even entry would be a code entry
    # assuming that code is always enclosed by ```
    for i in range(len(split_text)):
        if i > 0 and i % 2 == 1:
            # find programming language by going to first newline character
            language = split_text[i][:split_text[i].find('\n')]
            split_text[i] = get_code_formatted(code=split_text[i], language=language)
        else:
            split_text[i] = f"{Fore.LIGHTGREEN_EX}{Back.BLACK}{split_text[i]}{Style.RESET_ALL}"

    return ''.join(split_text)


def llm_call(LLM, conversation):

    # Unpack Langchain Conversation into openai call
    openai_spec_conversation = []
    for c in conversation:
        match c.role:
            case 'user':
                

    # add extra steps if needed
    from pprint import pprint
    print(type(conversation))
    pprint(vars(conversation[0]))
    pprint(LLM(conversation))
    return LLM(conversation).content


def grab_user_input(User:str = 'User') -> str:
    end_token = '//'  # /end

    grab_input = []
    while True:
        if not grab_input:
            grab_input.append(input(f'{Fore.LIGHTMAGENTA_EX}{Back.BLACK}{User}: '))
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


def execute_human_tasks(human_input: str, conversation: List[AIMessage]):
    if human_input.lower() in ['copy', 'copy to clipboard']:
        text_to_copy = conversation[-1].content
        pyperclip.copy(text_to_copy)
        print(f'{Fore.RED}\n\tCopied to clipboard!')
        print(f'Text Copied: {text_to_copy[:20]} ... {text_to_copy[-20:]}')
        return True
    elif human_input[:7] == 'spotify':
        llm_dj(music_request=human_input[7:])
        return True
    else:
        return False
