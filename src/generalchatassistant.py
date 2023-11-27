import pyperclip

from sdxl import llm_sdxl_chat
from spotify import llm_dj
from colorama import Fore

from openai import OpenAI

from chatbase import ChatBase
from arbitrary_cli_assistant import llm_cli_assistant

client = OpenAI()


class GeneralChatAssistant(ChatBase):

    def divert_execution(self, human_input: str):
        if human_input.lower() in ['copy', 'copy to clipboard']:
            text_to_copy = self.conversation[-1].content
            pyperclip.copy(text_to_copy)
            print(f'{Fore.RED}\n\tCopied to clipboard!')
            print(f'Text Copied: {text_to_copy[:20]} ... {text_to_copy[-20:]}')
            return True
        elif human_input[:7] == 'spotify':
            llm_dj(music_request=human_input[7:], debug=self.debug)
            return True
        elif human_input[:4] == 'sdxl':
            llm_sdxl_chat(img_request=human_input[4:], debug=self.debug)
            return True
        elif human_input[:len('cli')] == 'cli':
            llm_cli_assistant(cli_request=human_input[len('cli'):], debug=False)
            return True

        return False
