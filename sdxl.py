import argparse
import configparser

# Create a configuration object
config = configparser.ConfigParser()

# Read the configuration file
config.read('sd-xl-config.ini')

# Get the values from the configuration file
resources_directory = config.get('Paths', 'resources_directory')
output_save_directory = config.get('Paths', 'output_save_directory')

# Use the values in your script
print(f"Resources Directory: {resources_directory}")
print(f"Output Save Directory: {output_save_directory}")

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
It is a good practice to include a generic negative prompt.ugly, deform, disfigured
By adding specific keywords to the prompt, we can engineer the image to get the style we want.
Tips for good prompts:
Be detailed and specific when describing the subject.Use multiple brackets () to increase its strength and [] to reduce. Use an appropriate medium type consistent with the artist. E.g. photograph should not be used with van Gogh.The artist’s name is a very strong style modifier. Use wisely. Experiment with blending styles.

Example call:
python -m python_coreml_stable_diffusion.pipeline --prompt <prompt> --negative-prompt <negative_prompt> -o {output_save_directory} --guidance-scale 7.5 --num-inference-steps 25 --seed 23

--prompt <prompt>: prompt to generate an image of the object and in the style that you'd like
-o <output-dir>: output directory, default to {output_save_directory}
--negative-prompt <negative_prompt>: negative prompt for image generation.
--guidance-scale <guidance-scale>: default to 7.5 but if the user want something very aligned go up to ten.
--num-inference-steps <num_inference_steps>: number of steps for image generation, default to {25}

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


def llm_sdxl(img_request: str, debug=False):
    from cli_calls import CliLlmCalls

    spotify_cli_agent = CliLlmCalls(
        agent_name='SDXL',
        user_name='ImageRequest',
        orienting_system_message=SDXL_PROMPT,
        debug=debug
    )
    spotify_cli_agent.chat(initial_message=img_request)


if __name__ == '__main__':
    # get user question
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-r',
                        "--request",
                        type=str,
                        help="User Request")

    args = parser.parse_args()

    llm_sdxl(img_request=args.request, debug=True)
