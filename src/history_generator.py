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
                                          prompts:List[str]|None = None) -> Dict[str,Dict[str,str]]:
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
                base_dict_values:Dict[str,str] = None,
                model:str = model, t:float=temperature, logger:logging.Logger|None = None,
                prompts:List[str]|None = None, parser:List|None = None) -> Dict[str,str]:
    """
    Generates a review based on the best story. It typically adds text and makes the history more interesting.
    A single pass typically improves the story.

    Args:
        data (Dict[str,Dict[str,str]]): The input data for generating the review.
        api_key (str, optional): The API key for the OpenAI service. Defaults to openai_api_key.
        base_dict_values (Dict[str,str], optional): The base dictionary values. Defaults to None.
        model (str, optional): The model to use for generating the review. Defaults to model.
        t (float, optional): The temperature parameter for generating the review. Defaults to temperature.
        logger (logging.Logger|None, optional): The logger object for logging the review process. Defaults to None.
        prompts (List[str]|None, optional): The list of prompts for generating the review. Defaults to None.
        parser (List|None, optional): The parser object for formatting the review output. Defaults to None.

    Returns:
        Dict[str,str]: The generated review.
    """
    
    all_histories = select_best_histories_step_1(data)
    if prompts is None:
        prompts = pp.generate_base_prompt_review(all_histories, base_dict_values)

    if parser is None:
        parser = pp.prepare_answer_format_review(base_dict_values)
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

def make_prompt_images_after_review(data:Dict[str,Dict[str,str]], logger:logging.Logger|None = None,
                             base_dict_values:Dict[str,str]|None = None)-> Dict[str,Dict[str,str]]:
    """
    Generates image prompts for each history in the given data dictionary.
    It try to preserve overall story consistency and coherence.
    Without this step and based in the text only, the images could be not related to the story or between them.

    Args:
        data (Dict[str,Dict[str,str]]): A dictionary containing history data.
        logger (logging.Logger|None, optional): A logger object for logging messages. Defaults to None.
        base_dict_values (Dict[str,str]|None, optional): A dictionary containing base values for prompts. Defaults to None.

    Returns:
        Dict[str,Dict[str,str]]: A dictionary containing the updated data with image prompts.

    Raises:
        Exception: If there is an error while adding images for a history.
    """
    image_prompts = pp.generate_base_prompt_to_produce_image_prompt(data)
    parser = pp.prepare_answer_format_to_prompt_image(base_dict_values)
    output_parser, output_prompts = pp.generate_prompts(image_prompts, parser)
    data_image = llm_call_chain_for_history_generation(parser=output_parser, prompts=output_prompts)
    for history,image_description in data_image.items():
        try:
            for element, description in image_description.items():
                if 'image' in element:
                    data[history][element] = description
            if logger is not None:
                logger.info(f"Images for history {history} added")
        except Exception as e:
            if logger is not None:
                logger.error(f"Error while adding images for {history}: {e}")
            raise e
    return data
        
    

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
    # data = make_review(data, logger=logger)
    # PATH = r'C:\proyectos_personales\Cuentos\out_put_test\2024-03-26_22-30-44_histories.pkl'
    # with open(PATH, 'rb') as f:
    #     data = pickle.load(f)
    # image_prompts = pp.generate_base_prompt_to_produce_image_prompt(data)
    # parser = pp.prepare_answer_format_to_prompt_image()
    # output_parser, output_prompts = pp.generate_prompts(image_prompts, parser)
    # data = llm_call_chain_for_history_generation(logger=logger,
    #                                                 parser=output_parser, prompts=output_prompts)
    # with open(path, 'wb') as f:
        # pickle.dump(data, f)


    print("Done!")