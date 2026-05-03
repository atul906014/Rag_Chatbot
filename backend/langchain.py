from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
import os
load_dotenv()

client = InferenceClient(
    api_key=os.environ["HF_TOKEN"],
)

def call_hf(prompt_value):
    text = prompt_value.to_string()
    completion = client.chat.completions.create(
    model="MiniMaxAI/MiniMax-M2.5:novita",
    messages=[
        {
            "role": "user",
            "content": text,
        }
    ],
)
    return completion.choices[0].message.content

prompt = ChatPromptTemplate.from_template("Answer this: {question}")

# Wrap InferenceClient as a LangChain Runnable
chain = prompt | RunnableLambda(call_hf) | StrOutputParser()
for chunk in chain.stream([{"question": "What is the capital of France?"},
                          {"question": "What is Machine Learning?"}]):
    print(chunk, end="", flush=True)




