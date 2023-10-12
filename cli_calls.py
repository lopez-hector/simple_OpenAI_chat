import subprocess

from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    SystemMessage,
    AIMessage,
    HumanMessage
)
from utils import llm_call, get_formatted_text, grab_user_input
from colorama import Fore


class CliLlmCalls:
    def __init__(self,
                 agent_name: str,
                 orienting_system_message,
                 user_name: str = 'User',
                 model='gpt-4',
                 max_tokens=2000,
                 temperature=1,
                 debug=False
                 ):

        self.model = model
        self.LLM = ChatOpenAI(
            model_name=self.model,
            max_tokens=max_tokens,
            temperature=temperature
        )

        # this will orient the cli assistant to help you create the correct cli arguments
        self.system_message = SystemMessage(content=orienting_system_message)
        self.user_name = user_name
        self.agent_name = agent_name
        self.state = 'chat'
        self.debug = debug

    def chat(self, initial_message: str):
        self.state = 'chat'
        system_message_prompt = self.system_message
        conversation = [system_message_prompt, HumanMessage(content=initial_message)]
        output = llm_call(LLM=self.LLM, conversation=conversation)
        ai_message_prompt = self.process_llm_output(llm_output=output)
        conversation.append(ai_message_prompt)

        # continue chatting until a cli command is executed
        human_input = ''
        while human_input != 'quit' and self.state == 'chat':
            # human response
            human_input = grab_user_input(User=f'{self.user_name}: ')
            if human_input.lower() == 'quit':
                print(f'Exiting {self.agent_name} Chat')
                break

            # conversation update
            human_message = HumanMessage(content=human_input)
            conversation.append(human_message)
            conversation.append(SystemMessage(content='Remember to output JSON format.'))

            # LLM response
            output = llm_call(LLM=self.LLM, conversation=conversation)

            # Process response
            ai_message_prompt = self.process_llm_output(llm_output=output)
            conversation.append(ai_message_prompt)

    def process_llm_output(self, llm_output):
        """
        The LLM response could be a direct response to the user (chat) or a need to execute a call.
        Here we either continue the conversation or execute the desired call.

        :param llm_output: Dict[str, str]. Keys should be 'chat' or 'cli_call'
            direct output from the LLM in response to the conversation.
        :return:
            ai_message_prompt_: AI response to be shown to the user

        """
        if '{' in llm_output:
            if (llm_output[0] != '{' or llm_output[-1] != '}'):
                llm_output = llm_output[llm_output.find('{'):llm_output.rfind('}')+1]

            if ':' in llm_output:
                first_colon_idx = llm_output.find(':')
                clean_llm_output = llm_output[:first_colon_idx+1] + llm_output[first_colon_idx+1:].replace(':', '-')
        else:
            clean_llm_output = llm_output

        if self.debug:
            print('dirty')
            print(llm_output)
            print('clean')
            print(clean_llm_output)
        # the LLM doesnt always output the right format when chatting, so we can catch that error here
        try:
            output_json = eval(clean_llm_output)
        except:
            output_json = {'chat': clean_llm_output}

        # if the LLM wants to chat, continue the conversation
        if 'chat' in output_json:
            print('chat')
            # Show LLMs chat response
            print(get_formatted_text(output_json['chat']).replace('\n', '\n\t'))
            ai_message_prompt_ = AIMessage(content=output_json['chat'])

        # if the LLM wants to run a cli call, then execute
        elif 'cli_call' in output_json:
            # define response here
            print('cli_call')
            ai_executing_response = 'Here you go.'
            ai_message_prompt_ = AIMessage(content=ai_executing_response)
            print(f'{Fore.LIGHTCYAN_EX}{ai_executing_response}')

            # Execute comand
            # TODO: Error Handling
            if not self.debug:
                subprocess.run(output_json['cli_call'].split(' '), )
            else:
                print(output_json['cli_call'].split(' '))
            self.state = 'execute_cli_call'
        else:
            ai_executing_response = "Sorry I couldn't do that, please try again"
            ai_message_prompt_ = AIMessage(content=ai_executing_response)

        return ai_message_prompt_
