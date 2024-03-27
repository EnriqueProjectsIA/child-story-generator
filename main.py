from pathlib import Path
import sys
src_path = Path(__file__).parent / 'src'
logging_path = Path(__file__).parent / 'logging'
if not src_path.exists():
    raise FileNotFoundError(f"Directory {src_path} not found")
else:
    sys.path.append(str(src_path))
if not logging_path.exists():
    raise FileNotFoundError(f"Directory {logging_path} not found")
else:
    sys.path.append(str(logging_path))
import read_configuration as rc
import prepare_prompt as pp
import history_generator as hg
import image_generator as ig
import pdf_generator as pg
import pickle
import logger_code as lc
from datetime import datetime as dt

image_model = "dall-e-3"

def wrapper(use_logger:bool = False, save_data:bool = False):
    """
    This function generates a history, images, and a PDF.

    It calls the `llm_call_chain_for_history_generation` function to generate the history data,
    then calls the `generate_images_for_history` function to generate images using the history data and an image model,
    and finally calls the `generate_pdf` function to generate a PDF using the generated data.

    """
    identifier = dt.now().strftime("%Y_%m_%dT%H_%M_%S")
    path_save_data = Path(__file__).parent / "data"
    path_save_data.mkdir(exist_ok=True)
    path_save_data = path_save_data / f"{identifier}_data.pkl"
    logger = None
    if use_logger:
        logger = lc.configure_logger(identifier)

    print("Generating story...")
    data = hg.llm_call_chain_for_history_generation(logger=logger)
    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    print("Generating images...")
    data = ig.generate_images_for_history(data=data, model=image_model, logger=logger)
    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    print("Generating PDF...")
    pg.generate_pdf(data, logger=logger)

def wrapper_review(use_logger:bool = False, save_data:bool = False):
    """
    Executes the process of generating stories, reviewing them, generating images, and generating a PDF.

    Args:
        use_logger (bool, optional): Flag indicating whether to use a logger for logging. Defaults to False.
        save_data (bool, optional): Flag indicating whether to save the generated data. Defaults to False.
    """
    identifier = dt.now().strftime("%Y_%m_%dT%H_%M_%S")
    path_save_data = Path(__file__).parent / "data"
    path_save_data = path_save_data / f"{identifier}_data.pkl"
    logger = None
    
    if use_logger:
        logger = lc.configure_logger(identifier = identifier)


    base_dict_values = rc.history_base_values()
    output_parser, output_prompts = pp.generate_prompts_for_chain(4,base_dict_values)
    
    print("Generating multiple stories...")
    data = hg.llm_call_chain_for_history_generation(logger=logger,
                                                    parser=output_parser,
                                                    prompts=output_prompts)
    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    
    print("Reviewing best story...")
    data = hg.make_review(data, logger=logger)

    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    print("Generating prompts to produce images...")
    data = hg.make_prompt_images_after_review(data, logger=logger,
                                       base_dict_values=base_dict_values)
    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    print("Generating images...")
    data = ig.generate_images_for_history_after_review(data=data, model=image_model, logger=logger)
    if save_data:
        with open(path_save_data, "wb") as f:
            pickle.dump(data, f)
    print("Generating PDF...")
    pg.generate_pdf(data, logger=logger, identifier=identifier)


def main(review: bool = True, use_logger: bool = False, save_data: bool = False):
    """
    Main function for story generation process.

    Args:
        review (bool): Flag indicating whether to review the generated story (default is True).
        use_logger (bool): Flag indicating whether to use a logger for logging (default is False).
        save_data (bool): Flag indicating whether to save the generated data (default is False).
    """
    path_save_data = Path(__file__).parent / "data"
    path_save_images = Path(__file__).parent / "images"
    path_save_stories = Path(__file__).parent / "stories"
    path_save_data.mkdir(exist_ok=True)
    path_save_images.mkdir(exist_ok=True)
    path_save_stories.mkdir(exist_ok=True)

    if review:
        wrapper_review(use_logger=use_logger, save_data=save_data)
    else:
        wrapper(use_logger=use_logger, save_data=save_data)
    
    print("Story generation process finished")
    
if __name__ == "__main__":
    import argparse
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1', 'si', 's'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=str2bool, nargs='?', const=True, help="Run the review process", default=True)
    parser.add_argument("--use_logger", type=str2bool, nargs='?', const=True, default=True, help="Use the logger")
    parser.add_argument("--save_data", type=str2bool, nargs='?', const=True, default=True, help="Save the data")
    args = parser.parse_args()
    main(review=args.review, use_logger=args.use_logger, save_data=args.save_data)
