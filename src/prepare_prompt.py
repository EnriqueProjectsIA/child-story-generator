from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
import helper_functions as hf
from pathlib import Path
import random
from typing import Dict, Any
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
        "moral_values": moral_values,
        "story_genere": story_genere,
        "language": language,
        "pages": pages,
        "words_per_page": words_per_page,
        "questions": questions
    }

    return out_put



def base_prompt_template(child_name:str, number_of_years_child:int, topic:str,
                         moral_value:str, story_genere:str,
                         language:str, pages:int, words_per_page:int,
                         questions:int) -> str:
    """
    Generate a prompt for the story generator
    """
    base_prompt_template = f"""
    Eres el mejor contador de historias del mundo. Tu propósito es es escribir una historia para {child_name}.
    La historia debe tratar sobre el tema "{topic}" y enseñar una lección de moral acerca de "{moral_value}".
    La historia debe ser de género "{story_genere}". Y debe estar escrita en el idioma "{language}".
    Deberás tener en cuenta que la edad de {child_name} es {number_of_years_child} años. Adaptrás el lenguaje y
    la complejidad de la historia a su edad. La historia debe ser entretenida y educativa. La hsitória debe tener
    un inicio, un nudo y un desenlace. La historia debe ser original y creativa. La historia debe tener {pages} páginas.
    Cada página debe tener un máximo de {words_per_page} palabras. Si decides introducir a {child_name} en la historia,
    su nombre debe ser "{child_name}" con independencia del leguaje con el que escribas la historia.
    Después de escribir la historia, deberás escribir un título corto para la historia. 
    """
    if questions > 0:
        base_prompt_template += f"""
        Después de escribir la historia, deberás añadir {questions} preguntas sobre la historia.
        Las preguntas deben estar enfocadas a la comprensión de la historia y siempre deben tener en cuenta que
        la edad de {child_name} es {number_of_years_child} años.
        """
    return base_prompt_template

def base_prompt_template_image(child_name:str, number_of_years_child:int) -> str:
    base_prompt_template = f"""
    Estamos preparando una historia para {child_name}. {child_name} tiene una edad de {number_of_years_child} años.
    Necesitamos una imagen para la historia. Se trata de una imagen para colorear.
    La imagen debe ser de lineas simples y debe ser fácil de colorear. 
    La imagen no debe tener muchos detalles y debe ser fácil de entender.
    La imagen debe estar relacionada o inspirada en la siguiente frase perteneciente a la historia:
    """
    return base_prompt_template

def generate_base_prompt() -> str:
    """
    Generate a prompt for the story generator
    """
    base_dict_values = history_base_values()
    prompts = []
    for i, name in enumerate(base_dict_values["names"]):
        prompt = base_prompt_template(name, base_dict_values["number_of_years"][i], 
                                      random.choice(base_dict_values["topics"]),
                                      random.choice(base_dict_values["moral_values"]),
                                      random.choice(base_dict_values["story_genere"]),
                                      base_dict_values["language"],
                                      base_dict_values["pages"], base_dict_values["words_per_page"],
                                      base_dict_values["questions"])
        
        prompts.append(prompt)
    return prompts
def generate_base_prompt_image() -> str:
    """
    Generate a prompt for the story generator
    """
    base_dict_values = history_base_values()
    prompts = []
    for i, name in enumerate(base_dict_values["names"]):
        prompt = base_prompt_template_image(name, base_dict_values["number_of_years"][i])
        prompts.append(prompt)
    return prompts

def prepare_answer_format() -> ResponseSchema:
    """
    Prepare the answer format for the story generator
    """
    base_dict_values = history_base_values()
    number_of_pages = base_dict_values["pages"]
    questions = base_dict_values["questions"]
    response_schemas = []
    for i in range(number_of_pages):
        response_schemas.append(ResponseSchema(name=f"page_{i}",
                                               description=f"add text for page {i} of the story"))
    response_schemas.append(ResponseSchema(name="title",
                                           description="add a short title for the story"))
    if questions > 0:
        for i in range(questions):
            response_schemas.append(ResponseSchema(name=f"question_{i}",
                                                   description=f"add question {i} about the story"))
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser

def generate_prompts() -> PromptTemplate:
    """
    Prepare the prompt for the story generator
    """
    base_promts = generate_base_prompt()
    output_parser = prepare_answer_format()

    format_instructions = output_parser.get_format_instructions()
    output_prompts = []
    for base_prompt in base_promts: 
        prompt = PromptTemplate(
            template=f"{base_prompt} "+"\n{format_instructions}\n{question}",
            input_variables=["question"],
            partial_variables={"format_instructions": format_instructions},
        )
        output_prompts.append(prompt)
    return output_parser, output_prompts

if __name__ == "__main__":
    prompt = generate_base_prompt()
    print(prompt[0])