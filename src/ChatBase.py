import dataclasses
import subprocess
from typing import List

from utils import OpenAIFormat
from utils import get_formatted_text, grab_user_input
from colorama import Fore

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletionMessage
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
import abc

client = OpenAI()


class ChatBase:
    def __init__(self,
                 agent_name: str,
                 orienting_system_message,
                 user_name: str = 'User',
                 model='gpt-4-1106-preview',
                 return_json: bool = False,
                 max_tokens=2000,
                 temperature=1,
                 debug=False
                 ):

        self.model = model
        self.return_json = return_json

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
            message: ChatCompletionMessage = llm_response.choices[0].message
            response = self.process_llm_output(llm_message=message)
            self.conversation.append(response)

        # continue chatting until a cli command is executed
        human_input = ''
        while human_input != 'quit' and self.state == 'chat':
            # human response
            human_input = grab_user_input(User=f'{self.user_name}')

            executed: bool = self.divert_execution(human_input)
            if executed:
                print(self.state, human_input)
                continue

            if human_input.lower() == 'quit':
                print(f'Exiting {self.agent_name} Chat')
                break

            # conversation update
            human_message_prompt = OpenAIFormat(role='user', content=human_input)
            self.conversation.append(human_message_prompt)

            llm_response = self.llm_call()
            message: ChatCompletionMessage = llm_response.choices[0].message
            # print('MESSAGE')
            # print(message)
            response: OpenAIFormat = self.process_llm_output(llm_message=message)

            if response.content.lower().strip() == 'Have a nice day!!!'.lower():
                break

            self.conversation.append(response)
            # print('DEBUG')
            # [print(c.role, '\t', c.content) for c in self.conversation]

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

        if self.debug:
            print('AI RESPONSE')
            print(message_content)
        # TODO Tool calls
        tool_calls: List[ChatCompletionMessageToolCall] | None = llm_message.tool_calls


        # the LLM doesn't always output JSON when chatting, so we can catch that error here
        try:
            output_json = eval(message_content)
        except:
            output_json = {'chat': message_content}

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

        llm_args = {
            'model': self.model,
            'messages': openai_spec_conversation
        }

        if self.return_json:
            llm_args = llm_args | dict(response_format={"type": "json_object"})
        # call openai LLM
        response = client.chat.completions.create(
            **llm_args,
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

    @abc.abstractmethod
    def divert_execution(self, human_input: str) -> bool:
        """
        Take actions on human input before language model.
        e.g.
            1. Route to different models
            3. copy text to clipboard

        :param human_input:
        :return: if something was executed or not
        """
        raise NotImplemented
