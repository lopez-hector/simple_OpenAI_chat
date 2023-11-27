import dataclasses
from dataclasses import asdict
from typing import List, TypeAlias, Dict

import pyperclip
from langchain.schema import AIMessage
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from colorama import Fore, Back, Style

from openai import OpenAI

client = OpenAI()


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


def llm_call(conversation):
    openai_spec_conversation = []
    for c in conversation:
        openai_spec_conversation.append({k: v for k, v in asdict(c).items() if v is not None})

    # call openai LLM
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=openai_spec_conversation,
        # tools=None,
        # tool_choice="auto",  # auto is default, but we'll be explicit
    )

    return response


def grab_user_input(User: str = 'User') -> str:
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


FunctionCalled: TypeAlias = Dict[str, str]  # name, arguments
ToolCall: TypeAlias = Dict[str, str | FunctionCalled]  # id, type, function the model called


@dataclasses.dataclass
class OpenAIFormat:
    role: str
    content: str
    tool_calls: ToolCall | None = None


Conversation: TypeAlias = List[OpenAIFormat]
