import dataclasses
import subprocess
from typing import TypeAlias, List, Dict
import pyperclip

from sdxl import llm_sdxl_chat
from spotify import llm_dj
from utils import llm_call, get_formatted_text, grab_user_input
from colorama import Fore

from openai import OpenAI
from openai.types.chat.chat_completion import  ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

client = OpenAI()

FunctionCalled: TypeAlias = Dict[str, str]  # name, arguments
ToolCall: TypeAlias = Dict[str, str | FunctionCalled]  # id, type, function the model called


@dataclasses.dataclass
class OpenAIFormat:
    role: str
    content: str
    tool_calls: ToolCall | None = None


Conversation: TypeAlias = List[OpenAIFormat]


class CliLlmCalls:
    def __init__(self,
                 agent_name: str,
                 orienting_system_message,
                 user_name: str = 'User',
                 model='gpt-4-1106-preview',
                 max_tokens=2000,
                 temperature=1,
                 debug=False
                 ):

        self.model = model

        # this will orient the cli assistant to help you create the correct cli arguments
        self.system_message = OpenAIFormat(role='system', content=orienting_system_message)
        self.user_name = user_name
        self.agent_name = agent_name
        self.state = 'chat'
        self.debug = debug

        self.conversation = [self.system_message]

    def chat(self, initial_message: str | None = None):

        if initial_message is not None:
            self.state = 'chat'
            self.conversation.append(OpenAIFormat(role='user', content=initial_message))
            llm_response = self.llm_call()
            response = self.process_llm_output(llm_message=llm_response.message)
            self.conversation.append(response)

        # continue chatting until a cli command is executed
        human_input = ''
        while human_input != 'quit' and self.state == 'chat':
            # human response
            human_input = grab_user_input(User=f'{self.user_name}')
            executed: bool = self.execute_human_tasks(human_input, self.conversation)

            if executed:
                continue

            if human_input.lower() == 'quit':
                print(f'Exiting {self.agent_name} Chat')
                break

            # conversation update
            human_message_prompt = OpenAIFormat(role='user', content=human_input)
            self.conversation.append(human_message_prompt)

            llm_response = self.llm_call()
            message: ChatCompletionMessage = llm_response.choices[0].message

            response: OpenAIFormat = self.process_llm_output(llm_message=message)

            if response.content.lower().strip() == 'Have a nice day!!!'.lower():
                break

            self.conversation.append(response)

        print('EXITING')

    def process_llm_output(self, llm_message: ChatCompletionMessage) -> OpenAIFormat:
        """
        The LLM response could be a direct response to the user (chat) or a need to execute a call.
        Here we either continue the conversation or execute the desired call.

        :param llm_message: Dict[str, str]. Keys should be 'chat' or 'cli_call'
            direct output from the LLM in response to the conversation.
        :return:
            ai_message_prompt_: AI response to be shown to the user

        """
        message_content = llm_message.content

        # TODO Tool calls
        tool_calls: List[ChatCompletionMessageToolCall] | None = llm_message.tool_calls

        # Hacky way to extract poorly formatted json output from models
        if '{' in message_content:
            if message_content[0] != '{' or message_content[-1] != '}':
                message_content = message_content[message_content.find('{'):message_content.rfind('}') + 1]

            if ':' in message_content:
                first_colon_idx = message_content.find(':')
                clean_llm_output = message_content[:first_colon_idx + 1] + message_content[first_colon_idx + 1:].replace(':', '-')
        else:
            clean_llm_output = message_content

        # the LLM doesn't always output JSON when chatting, so we can catch that error here
        try:
            output_json = eval(clean_llm_output)
        except:
            output_json = {'chat': clean_llm_output}

        # if the LLM wants to chat, continue the conversation
        if 'chat' in output_json:
            print('chat')
            # Show LLMs chat response
            print(get_formatted_text(output_json['chat']).replace('\n', '\n\t'))
            ai_message_prompt_ = OpenAIFormat(role='assistant', content=output_json['chat'])
        # if the LLM wants to run a cli call, then execute
        elif 'cli_call' in output_json:
            # define response here
            print('cli_call')
            # Execute comand
            # TODO: Error Handling
            ai_message_prompt_ = self.cli_call(output_json['cli_call'])
        else:
            ai_executing_response = "Sorry I couldn't do that, please try again"
            ai_message_prompt_ = OpenAIFormat(role='assistant', content=ai_executing_response)

        return ai_message_prompt_

    def llm_call(self, conversation=None):

        if conversation is None:
            conversation = self.conversation

        openai_spec_conversation = []
        for c in conversation:
            openai_spec_conversation.append({k: v for k, v in dataclasses.asdict(c).items() if v is not None})

        # call openai LLM
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=openai_spec_conversation,
            response_format={"type": "json_object"},
            # tools=None,
            # tool_choice="auto",  # auto is default, but we'll be explicit
        )

        return response

    def cli_call(self, cli_call) -> OpenAIFormat:
        self.state = 'execute_cli_call'

        ai_executing_response = 'Here you go.'
        ai_message_prompt = OpenAIFormat(role='assistant', content=ai_executing_response)
        print(f'{Fore.LIGHTCYAN_EX}{ai_executing_response}')

        if not self.debug:
            subprocess.run(cli_call.split(' '), )
        else:
            print(cli_call)

        return ai_message_prompt

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
