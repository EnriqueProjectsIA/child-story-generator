from pathlib import Path
from langchain_openai import ChatOpenAI
import prepare_prompt as pp
from dotenv import load_dotenv
import os
from datetime import datetime as dt
import logging
import helper_functions as hf
import prepare_prompt as pp
from typing import List,Dict
path = Path(__file__).parent / ".env"
load_dotenv(path)
# Load the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
model = "gpt-4-0125-preview"
temperature = 0.5

def llm_call_chain_for_history_generation(api_key:str = openai_api_key,
                                          model:str = model,
                                          t:float=temperature,
                                          logger:logging.Logger|None = None,
                                          parser:str|None = None,
                                          prompts:List[str]|None = None) -> dict:
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
    #case condition
    
    if parser is None and prompts is None:
        output_parser, output_prompts = pp.generate_prompts()
        parser = output_parser
        prompts = output_prompts

    out_put_histories = {}
    for i, prompt in enumerate(prompts):
        chain = prompt | llm | parser
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
                for k,v in result.items():
                    logger.info(f"{k}: {v}")
        except Exception as e:
            if logger is not None:
                logger.error(f"Error while saving history: {e}")
            raise e
    return out_put_histories

def select_best_histories_step_1(data:Dict[str,Dict[str,str]]) -> Dict[str,str]:
    """
    Select the best history from a dictionary of histories

    Parameters:
    - data (Dict): A dictionary containing the generated histories.

    Returns:
    - best_histories (Dict[str,str]): A dictionary containing the best histories.
    """
    best_histories = {}
    for i,(k, history_data) in enumerate(data.items()):
        best_history = hf.select_best_history(history_data)
        new_key = f"history_{i}"
        best_histories[new_key] = best_history
    return best_histories

def make_review(data:Dict[str,Dict[str,str]], api_key:str = openai_api_key,
                model:str = model, t:float=temperature, logger:logging.Logger|None = None,
                prompts:List[str]|None = None, parser:List|None = None) -> Dict[str,str]:
    
    all_histories = select_best_histories_step_1(data)
    if prompts is None:
        prompts = pp.generate_base_prompt_review(all_histories)

    if parser is None:
        parser = pp.prepare_answer_format_review()
    output_parser, output_prompts = pp.generate_prompts(prompts, parser)
    if logger is not None:
        logger.info("Review started")
        logger.info(output_prompts)
        
    result = llm_call_chain_for_history_generation(api_key=api_key, model=model, t=t, logger=logger,
                                                   parser=output_parser, prompts=output_prompts)
    if logger is not None:
        logger.info("Review completed")
        for k,v in result.items():
            logger.info(f"{k}: {v}")
    return result

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
    output_parser, output_prompts = pp.generate_prompts_for_chain(4)
    data = llm_call_chain_for_history_generation(logger=logger,
                                                 parser=output_parser, prompts=output_prompts)
    data = make_review(data, logger=logger)
    with open(path, 'wb') as f:
        pickle.dump(data, f)


    print("Done!")