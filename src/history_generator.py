from pathlib import Path
from langchain_openai import ChatOpenAI
import prepare_prompt as pp
from dotenv import load_dotenv
import os
from datetime import datetime as dt
import logging
path = Path(__file__).parent / ".env"
load_dotenv(path)
# Load the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
model = "gpt-4-0125-preview"
temperature = 0.5

def llm_call_chain_for_history_generation(api_key:str = openai_api_key,
                                          model:str = model,
                                          t:float=temperature,
                                          logger:logging.Logger|None = None) -> dict:
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
        try:
            result = chain.invoke({"question": "Prepara una historia de acuerdo a las instrucciones"})
        except Exception as e:
            if logger is not None:
                logger.error(f"Error while generating history: {e}")
            result = {"error": str(e)}
        try:
            out_put_histories[f"history_{i}"] = result
            if logger is not None:
                logger.info(f"History {i} generated successfully")
        except Exception as e:
            if logger is not None:
                logger.error(f"Error while saving history: {e}")
            raise e
    return out_put_histories



if __name__ == "__main__":
    import sys
    log_path = Path(__file__).parent.parent / 'logging'
    if not log_path.exists():
        raise FileNotFoundError(f"Directory {log_path} not found")
    else:
        sys.path.append(str(log_path))
    import pickle
    import logger_code as lc
    logger = lc.configure_logger()
    now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = f'out_put_test/{now}_histories.pkl'
    data = llm_call_chain_for_history_generation(logger=logger)
    with open(path, 'wb') as f:
        pickle.dump(data, f)

    print("Done!")