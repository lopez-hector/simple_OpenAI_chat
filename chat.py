from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessage,
    AIMessagePromptTemplate,
    HumanMessage,
)

import openai
from pathlib import Path
import argparse

def main(model: str = 'gpt-3.5-turbo'):

    LLM = ChatOpenAI(model_name=model, max_tokens=2000)

    # what should the model do with your input
    conversation = []
    human_input = ''
    while human_input != 'quit':
        # convert to format for model

        human_input = input('User: ')

        if human_input.lower() == 'quit':
            print('EXITING')
            break

        human_message_prompt = HumanMessage(content=human_input)
        conversation.append(human_message_prompt)
        chat_prompt = ChatPromptTemplate.from_messages(conversation)

        # run as a chain
        chain = LLMChain(llm=LLM, prompt=chat_prompt, )
        output = chain.run(input_language="English")

        system_message_prompt = SystemMessage(content=output)
        conversation.append(system_message_prompt)
        print(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-m',
                        "--model_name",
                        type=str,
                        help="Name of the model")

    args = parser.parse_args()

    acceptable_models = set(['gpt-4', 'gpt-3.5-turbo'])

    # Call the main function and pass the model_name argument
    if args.model_name and args.model_name in acceptable_models:
        main(model=model_name)
    else:
        print('defaulting to chat-gpt (gpt-3.5-turbo)')
        main(model='gpt-3.5-turbo')
