from typing import Dict, Any
from pathlib import Path
import helper_functions as hf
import configparser

def history_base_values(path:str|None = None) -> Dict[str, Any]:
    """
    Read the base values for the history generator
    """
    config = configparser.ConfigParser()
    if not path:
        path = Path(__file__).parent.parent / "configuration.ini"
    if not Path(path).exists():
        raise FileNotFoundError(f"File {path} not found")
    config.read(path)
    names = [i.strip().lower().capitalize() for i in config["childs"]["NAMES"].split(",")]
    birthdays = [i.strip() for i in config["childs"]["BIRTHDAYS"].split(",")]
    number_of_years = [ hf.calculate_number_of_years(date) for date in birthdays]
    topics = [i.strip().lower() for i in config["history"]["TOPICS"].split(",")]
    include_moral_values = config["history"]["INCLUDE_MORAL_VALUES"].strip().lower() == "true"
    moral_values = [i.strip().lower() for i in config["history"]["MORAL_VALUES"].split(",")]
    story_genere = [i.strip().lower() for i in config["history"]["STORY_GENERE"].split(",")]
    language = config["book"]["LANGUAGE"].strip().lower().capitalize()
    pages = int(config["book"]["PAGES"])
    words_per_page = int(config["book"]["WORDS_PER_PAGE"])
    questions = int(config["activity"]["QUESTIONS"])

    out_put = {
        "names": names,
        "birthdays": birthdays,
        "number_of_years": number_of_years,
        "topics": topics,
        "include_moral_values": include_moral_values,
        "moral_values": moral_values,
        "story_genere": story_genere,
        "language": language,
        "pages": pages,
        "words_per_page": words_per_page,
        "questions": questions
    }

    return out_put
