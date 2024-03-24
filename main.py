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



def wrapper():
    data = hg.llm_call_chain_for_history_generation()
    data = ig.generate_images_for_history(data=data)
    pg.generate_pdf(data)

if __name__ == "__main__":
    wrapper()