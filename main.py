from pathlib import Path
import sys
src_path = Path(__file__).parent / 'src'
if not src_path.exists():
    raise FileNotFoundError(f"Directory {src_path} not found")
else:
    sys.path.append(str(src_path))

import history_generator as hg
import image_generator as ig
import pdf_generator as pg

image_model = "dall-e-3"

def wrapper():
    print("Generating history...")
    data = hg.llm_call_chain_for_history_generation()
    print("Generating images...")
    data = ig.generate_images_for_history(data=data, model=image_model)
    print("Generating PDF...")
    pg.generate_pdf(data)


if __name__ == "__main__":
    wrapper()