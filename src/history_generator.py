from langchain_openai import ChatOpenAI
import prepare_prompt as pp
from dotenv import load_dotenv
import os
from pathlib import Path
import json
from datetime import datetime as dt
path = Path(__file__).parent / ".env"
load_dotenv(path)
# Load the environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(api_key=openai_api_key, model = "gpt-4-0125-preview", temperature=0.6)
output_parser, output_prompts = pp.generate_prompts()
out_put_histories = {}
for i, prompt in enumerate(output_prompts):
    chain = prompt | llm | output_parser
    result = chain.invoke({"question": "Prepara una historia de acuerdo a las instrucciones"})
    out_put_histories[f"history_{i}"] = result
now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")
save_path = Path(__file__).parent.parent / "data" / f"{now}_histories.json"

with open(save_path, "w", encoding="utf-8") as f:
    json.dump(out_put_histories, f, indent=3)
    
    



if __name__ == "__main__":
    print("Done!")