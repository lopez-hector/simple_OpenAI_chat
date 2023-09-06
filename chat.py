from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessage,
    AIMessagePromptTemplate,
    AIMessage,
    HumanMessage,
)
import argparse
from utils import get_formatted_text


def main(model: str = 'gpt-3.5-turbo'):
    LLM = ChatOpenAI(model_name=model, max_tokens=2000)

    system_message_prompt = SystemMessage(
        content="I'm a helpful assistant. If the user has no further questions or the conversation has clearly ended I will expcitly return the phrase: ```Have a nice day!!!``` without any added text.")

    # what should the model do with your input
    conversation = [system_message_prompt]
    human_input = ''
    while human_input != 'quit':
        # convert to format for model
        grab_input = []
        while True:
            if not grab_input:
                grab_input.append(input('User: '))
            else:
                grab_input.append(input(''))

            if grab_input[-1] == '/end':
                grab_input.pop()
                break
            elif grab_input[-1][-4:] == '/end':
                grab_input[-1] = grab_input[-1][:-4]
                break
            elif grab_input[-1] == 'quit':
                grab_input = ['quit']
                break

        human_input = ''.join(grab_input)

        if human_input.lower() == 'quit':
            print('EXITING')
            break

        human_message_prompt = HumanMessage(content=human_input)
        conversation.append(human_message_prompt)
        chat_prompt = ChatPromptTemplate.from_messages(conversation)

        # run as a chain
        chain = LLMChain(llm=LLM, prompt=chat_prompt, )
        output = chain.run(input_language="English")

        print('\n', get_formatted_text(output))

        if output.lower().strip() == 'Have a nice day!!!'.lower():
            print('EXITING')
            break

        ai_message_prompt = AIMessage(content=output)
        conversation.append(ai_message_prompt)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Open AI chat")

    # Add the model_name argument
    parser.add_argument('-m',
                        "--model_name",
                        type=str,
                        help="Name of the model")

    args = parser.parse_args()

    acceptable_models = {'gpt-4', 'gpt-3.5-turbo'}

    # Call the main function and pass the model_name argument
    if args.model_name and args.model_name in acceptable_models:
        main(model=args.model_name)
    else:
        print('defaulting to chat-gpt (gpt-3.5-turbo)')
        main(model='gpt-3.5-turbo')
