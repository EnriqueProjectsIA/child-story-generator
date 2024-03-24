import prepare_prompt as pp
from dotenv import load_dotenv
import os
from typing import Dict, Any
import pickle
from openai import OpenAI

openai_api_key = os.getenv('OPENAI_API_KEY')
model = "dall-e-3"

def generate_images_for_history(api_key = openai_api_key,
                               model = model,
                               data:Dict[str,Any]|None=None):
    """
    Generates images for the history.

    Args:
        api_key (str): The OpenAI API key.
        model (str): The OpenAI model to use for generating images.
        data (Dict[str,Any]|None): The history to generate images for.

    Returns:
        Dict[str,Any]: The updated history with image URLs.

    """
    client = OpenAI(api_key=api_key)
    base_dict_values = pp.history_base_values()
    number_of_pages = base_dict_values["pages"]
    base_prompt_template_images = pp.generate_base_prompt_image()
    for i, (key,history) in enumerate(data.items()):
        for j in range(number_of_pages-1):
            base_prompt = base_prompt_template_images[i]      
            reference_text = history[f"page_{j}"]
            final_prompt = base_prompt+reference_text
            response = client.images.generate(
                model=model,
                prompt=final_prompt,
                response_format="b64_json",
                size="1024x1024",
                quality="standard",
                n=1,
            )
            data[key][f"image_{j}"] = response.data[0].b64_json
    return data
if __name__ == "__main__":
    # path = r'C:\proyectos_personales\Cuentos\data\2024-03-24_11-58-45_histories.pkl'
    # with open(path, 'rb') as f:
    #     data = pickle.load(f)
    # data = generate_images_for_history(data=data)
    new_path = r'C:\proyectos_personales\Cuentos\data\2024-03-24_11-58-45_histories_images.pkl'
    # with open(new_path, 'wb') as f:
    #     pickle.dump(data, f)
    with open(new_path, 'rb') as f:
        data = pickle.load(f)
    print(data)
    print("Done!")