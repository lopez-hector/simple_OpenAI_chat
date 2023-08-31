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

LLM = ChatOpenAI(model_name="gpt-4", max_tokens=2000)

# what should the model do with your input
conversation = []
human_input = ''
while human_input != 'quit':
    # convert to format for model

    human_input = input('User: ')
    human_message_prompt = HumanMessage(content=human_input)
    conversation.append(human_message_prompt)
    chat_prompt = ChatPromptTemplate.from_messages(conversation)

    # run as a chain
    chain = LLMChain(llm=LLM, prompt=chat_prompt, )
    output = chain.run(input_language="English")

    system_message_prompt = SystemMessage(content=output)
    conversation.append(system_message_prompt)
    print(output)
