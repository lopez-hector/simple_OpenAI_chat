from langchain import LLMChain
from langchain.prompts import ChatPromptTemplate
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_style_by_name
from pygments.lexers import get_lexer_by_name
from colorama import Fore, Back, Style
import openai


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
    chat_prompt = ChatPromptTemplate.from_messages(conversation)
    # run as a chain
    chain = LLMChain(llm=LLM, prompt=chat_prompt, )
    output = chain.run(input_language="English")
    return output


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
