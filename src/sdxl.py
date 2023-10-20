import argparse
import configparser
import subprocess
from pathlib import Path
from typing import Dict

from langchain.prompts.chat import (
    AIMessage,
)

from colorama import Fore
from cli_calls import CliLlmCalls

# use shpotify to cli control spotify
cli_docs = f"""

How to come up with good prompts for Stable Diffusion 
By understanding how to construct clear and concise prompts, you can unlock the whole range of style Stable Diffusion offers. To excel in prompt building, you should start with a specific subject in mind and add keywords to steer towards a particular effect.

Anatomy of a good prompt:
This is a proven techniques to generate high-quality, specific images. Your prompt should cover most, if not all, of these areas:
1. Subject (required) 
2. Medium 
3. Style 
4. Artist 
5. Resolution. 
Additional details: a. Color b. Lighting

First, you will need a subject description with as much detail as possible. Example: Prompt (subject only):A young woman with light blue dress sitting next to a wooden window reading a book. 

Provide as much detail as possible.
It is a good practice to include a generic negative prompt. Example: ugly, deform, disfigured
By adding specific keywords to the prompt, we can engineer the image to get the style we want.
Tips for good prompts:
Be detailed and specific when describing the subject.Use multiple brackets () to increase its strength and [] to reduce. Use an appropriate medium type consistent with the artist. E.g. photograph should not be used with van Gogh.The artist’s name is a very strong style modifier. Use wisely. Experiment with blending styles.

Example call:
python pipeline.py --prompt <prompt> --negative-prompt <negative_prompt> --guidance-scale 7.5 --num-inference-steps 25 --seed 5893757

Acceptable CLI args:

--prompt <prompt>: prompt to generate an image of the object and in the style that you'd like
--negative-prompt <negative_prompt>: negative prompt for image generation.
--guidance-scale <guidance-scale>: default to 7.5 but if the user want something very aligned go up to ten.
--num-inference-steps <num_inference_steps>: number of steps for image generation, default to {25}

only discuss guidance scale and num inference steps if discussed by user.

"""

RECURRING_PROMPT = """
If i can return a valid CLI call to fullfill the request i will return ONLY the cli_call in the following format:

return JSON:
    {"cli_call": "CLI_CALL"}
    
If i need more info to make a valid cli_call:

return JSON:
    {"chat": "chat"}
    
return JSON
"""

SDXL_PROMPT = f"""
RETURN JSON
I am a helpful agent that helps you construct images during image generation using a CLI interface. I will help you construct a useful and effective prompt from your ideas. When we agree on a prompt i will launch the image generation via the cli.

I will always return JSON with either a 'chat' or 'cli_call' key. 

RETURN JSON
CLI_DOCUMENTATION:
{cli_docs}
RETURN JSON
{RECURRING_PROMPT}"""


def get_config():
    # Create a configuration object
    config = configparser.ConfigParser()

    # Read the configuration file
    config.read('/Users/hectorlopezhernandez/PycharmProjects/chat/sd-xl-config.ini')

    # Get the values from the configuration file
    resources_directory = config.get('Paths', 'resources_directory')
    output_save_directory = config.get('Paths', 'output_save_directory')
    python_script_directory = config.get('Paths', 'python_script_directory')

    # Use the values in your script
    print(f"Resources Directory: {resources_directory}")
    print(f"Output Save Directory: {output_save_directory}")

    print(type(config))

    config = dict(resources_directory=resources_directory, output_save_directory=output_save_directory)

    return config


class SdxlCliLlmCalls(CliLlmCalls):
    def cli_call(self, cli_call: str):
        self.state = 'chat'  # continue chatting even after executing this

        config: Dict = get_config()

        default_args = {
            '--model-version': 'stabilityai/stable-diffusion-xl-base-1.0',
            '--compute-unit': 'CPU_AND_GPU',
            '-i': config['resources_directory'],
            '-o': config['output_save_directory']
        }

        import shlex
        parsed_command = shlex.split(cli_call)

        parsed_command.extend([split for kv in default_args.items() for split in kv])
        command_list = parsed_command[1:]

        # Formulate ai response
        ai_executing_response = f'''Running:\n```{cli_call}```'''

        ai_message_prompt = AIMessage(content=ai_executing_response)
        print(f'{Fore.LIGHTCYAN_EX}{ai_executing_response}')

        if not self.debug:
            print('\nList')
            print(command_list)
            try:
                subprocess.run(command_list, )
                from PIL import Image
                # Specify the path to your image file
                import os
                import glob

                def get_most_recent_file(directory):
                    os.chdir(directory)
                    files = sorted(glob.glob("*/*"), key=os.path.getctime, reverse=True)
                    if files:
                        return files[0]
                    else:
                        return None

                directory_path = default_args['-o']
                most_recent_file = Path(get_most_recent_file(directory_path))
                # Open the image file
                image = Image.open(Path(directory_path) / most_recent_file)

                # Display the image
                image.show()
            except:
                raise  # TODO

        else:
            print('string')
            print(cli_call)

            print('\nList')
            print(command_list)

        return ai_message_prompt


def llm_sdxl(img_request: str, debug=False):
    sdxl_agent = SdxlCliLlmCalls(
        agent_name='SDXL',
        user_name='ImageRequest',
        orienting_system_message=SDXL_PROMPT,
        debug=debug
    )

    sdxl_agent.chat(initial_message=img_request)


if __name__ == '__main__':
    # get user question
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-r',
                        "--request",
                        type=str,
                        required=True,
                        help="User Request")

    args = parser.parse_args()

    llm_sdxl(img_request=args.request, debug=False)
