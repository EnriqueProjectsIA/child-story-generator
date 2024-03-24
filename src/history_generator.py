from langchain_openai import ChatOpenAI
import prepare_prompt as pp
from dotenv import load_dotenv
import os
from pathlib import Path
import json
from datetime import datetime as dt
import pickle
path = Path(__file__).parent / ".env"
load_dotenv(path)
# Load the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
model = "gpt-4-0125-preview"
temperature = 0.5

def llm_call_chain_for_history_generation(api_key = openai_api_key,
                                          model = model,
                                          t=temperature):
    """
    Generates a call chain for history generation using the ChatOpenAI class.

    Parameters:
    - api_key (str): The API key for OpenAI.
    - model (str): The model to use for generating the history.
    - t (float): The temperature parameter for generating the history.

    Returns:
    - out_put_histories (dict): A dictionary containing the generated histories.

    """
    llm = ChatOpenAI(api_key=api_key, model=model, temperature=t)
    output_parser, output_prompts = pp.generate_prompts()
    out_put_histories = {}
    for i, prompt in enumerate(output_prompts):
        chain = prompt | llm | output_parser
        result = chain.invoke({"question": "Prepara una historia de acuerdo a las instrucciones"})
        out_put_histories[f"history_{i}"] = result
    return out_put_histories



if __name__ == "__main__":
    now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f'data/{now}_histories.pkl'
    data = llm_call_chain_for_history_generation()
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    print("Done!")