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
import history_generator as hg
import image_generator as ig
import pdf_generator as pg
import logger_code as lc

image_model = "dall-e-3"

def wrapper(use_logger:bool = False):
    """
    This function generates a history, images, and a PDF.

    It calls the `llm_call_chain_for_history_generation` function to generate the history data,
    then calls the `generate_images_for_history` function to generate images using the history data and an image model,
    and finally calls the `generate_pdf` function to generate a PDF using the generated data.

    """
    logger = None
    if use_logger:
        logger = lc.configure_logger()

    print("Generating history...")
    data = hg.llm_call_chain_for_history_generation(logger=logger)
    print("Generating images...")
    data = ig.generate_images_for_history(data=data, model=image_model, logger=logger)
    print("Generating PDF...")
    pg.generate_pdf(data, logger=logger)


if __name__ == "__main__":
    wrapper(use_logger=True)