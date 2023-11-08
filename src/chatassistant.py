import dataclasses

import pyperclip
from colorama import Fore
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessage,
    AIMessage,
    HumanMessage,
)

from typing import List, Union, Dict, TypeAlias, Optional

from spotify import llm_dj
from sdxl import llm_sdxl_chat
from utils import get_formatted_text, grab_user_input, llm_call

FunctionCalled: TypeAlias = Dict[str, str]  # name, arguments
ToolCall: TypeAlias = Dict[str, str, FunctionCalled]  # id, type, function the model called


@dataclasses.dataclass
class OpenAIFormat:
    role: str
    content: str
    tool_calls: ToolCall | None = None


Conversation: TypeAlias = List[OpenAIFormat]


class ChatAssistant:
    def __init__(
            self,
            orienting_message: str,
            LLM=ChatOpenAI(model_name='gpt-3.5-turbo', max_tokens=2000),
    ):

        self.LLM = LLM
        self.system_message_prompt: str = orienting_message
        self.conversation: Conversation = [OpenAIFormat(role='system', content=orienting_message)]

    @staticmethod
    def execute_human_tasks(human_input: str, conversation: Conversation):
        if human_input.lower() in ['copy', 'copy to clipboard']:
            text_to_copy = conversation[-1].content
            pyperclip.copy(text_to_copy)
            print(f'{Fore.RED}\n\tCopied to clipboard!')
            print(f'Text Copied: {text_to_copy[:20]} ... {text_to_copy[-20:]}')
            return True
        elif human_input[:7] == 'spotify':
            llm_dj(music_request=human_input[7:])
            return True
        elif human_input[:4] == 'sdxl':
            llm_sdxl_chat(img_request=human_input[4:], debug=False)
            return True
        else:
            return False

    def chat(self):
        human_input = ''
        while human_input != 'quit':
            human_input = grab_user_input()
            executed: bool = self.execute_human_tasks(human_input, self.conversation)

            if executed:
                continue
            if human_input.lower() == 'quit':
                print('EXITING')
                break

            human_message_prompt = OpenAIFormat(role='user', content=human_input)

            self.conversation.append(human_message_prompt)

            output = llm_call(self.LLM, self.conversation)
            print('  ', get_formatted_text(output).replace('\n', '\n  '))
            if output.lower().strip() == 'Have a nice day!!!'.lower():
                print('EXITING')
                break
            ai_message_prompt = AIMessage(content=output)
            self.conversation.append(ai_message_prompt)
