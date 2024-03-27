from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
import helper_functions as hf
from read_configuration import history_base_values
from pathlib import Path
import random
from typing import Dict, Any, List



def base_prompt_template(child_name:str, number_of_years_child:int, topic:str,
                         include_moral_values:bool, moral_value:str, story_genere:str,
                         language:str, pages:int, words_per_page:int,
                         questions:int) -> str:
    """
    Generate a prompt for the story generator
    """
    if include_moral_values:
        moral = f""" 
        y enseñar una lección de moral acerca de "{moral_value}"
        """
    else:
        moral = ""

    base_prompt_template = f"""
    Eres el mejor contador de historias del mundo. Tu propósito es es escribir una historia para {child_name}.
    La historia debe tratar sobre el tema "{topic}" {moral}".
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

def base_prompt_template_for_chain(child_name:str, number_of_years_child:int, topic:str,
                         include_moral_values:bool, moral_value:str, story_genere:str,
                         language:str, pages:int, words_per_page:int, number_of_histories:int) -> str:
    """
    Generate a prompt for the story generator
    """
    if include_moral_values:
        moral = f""" 
        y enseñar una lección de moral acerca de "{moral_value}"
        """
    else:
        moral = ""

    base_prompt_template = f"""
    Eres el mejor contador de historias del mundo. Tu propósito es es escribir una historias para {child_name}.
    Las historias deben tratar sobre el tema "{topic}" {moral}".
    Las historias deben ser de género "{story_genere}". Y deben estar escritas en el idioma "{language}".
    Deberás tener en cuenta que la edad de {child_name} es {number_of_years_child} años. Adaptrás el lenguaje y
    la complejidad de las historias a su edad. Las historias deben ser entretenidas y educativas. Las hsitorias deben tener
    un inicio, un nudo y un desenlace. Las historias deben ser originales y creativas. Las historias deben tener {pages} páginas.
    Cada página debe tener un máximo de {words_per_page} palabras. Si decides introducir a {child_name} en la historia,
    su nombre debe ser "{child_name}" con independencia del leguaje con el que escribas la historia. Pero {child_name}
    no debe ser el protagonista de todas las historias.
    Escribirás un total de {number_of_histories} historias.
    Después de escribir las historias razonarás paso a paso cuál es la mejor historia para {child_name}. Teniendo en cuenta
    la claridad, la coherencia, la originalidad y la creatividad de las historias.
    Por último, deberás dar el número de la mejor historia para {child_name}. La numeración empieza desde 0.
    """
    return base_prompt_template

def review_best_history_template(text:str,language:str, number_of_years_child:int,
                                 number_of_words:int, questions:int,
                                 other_histories:str|None = None) -> str:
    """
    Generate a prompt for the review story generator
    """
    review_prompt = f"""
    Eres un experto revisando historias y hablas en {language}. Tus revisiones son muy importantes para mejorar las historias.
    Cuando escribas tu historia revisada lo harás en el idioma "{language}". Cuando escribas tus
    raznomien
    """
    if other_histories is not None:
        review_prompt += f"""
        Estos son ejemplos de historias que has revisado:
        {other_histories}


        Para tu revisión de la historia, tendrás en cuenta las historias anteriores para asegurar la variedad en el vocabulario y el contenido de las historias.
        También evitarás repeticiones de palabras, frases y nombres de personajes. 
        """
    review_prompt += f"""
    Revisarás la historia para asegurar su calidad y adecuación a la edad de {number_of_years_child} años.
    Procura que la historia sea entretenida y educativa. La revisión será razonada y paso a paso.
    Es importante que en tu revisión cuentes el número de palabras en cada página. 
    Despues de revisar la historia reescribirás las páginas que consideres necesarias y te asegurarás de que
    cada página tenga entre {number_of_words-5} palabras y {number_of_words+5}.
    También añadirás un título apropiado para la historia. 
    El Texto a revisar es el siguiente:
    {text} 
    """
    if questions > 0:
        review_prompt += f"""
        Después de escribir la historia, deberás añadir {questions} preguntas sobre la historia.
        Las preguntas deben estar enfocadas a la comprensión de la historia y siempre deben tener en cuenta que
        la edad de la persona es {number_of_years_child} años.
        """
    review_prompt += f"""
    Recuerda escribir todo en el idioma "{language}".
    """
    return review_prompt

def base_prompt_template_image(child_name:str, number_of_years_child:int) -> str:
    """
    Generate a prompt for the images in the story
    """
    base_prompt_template = f"""
    Estamos preparando una historia para {child_name}. {child_name} tiene una edad de {number_of_years_child} años.
    Necesitamos una imagen para la historia. Se trata de una imagen para colorear.
    La imagen debe ser de lineas simples y debe ser fácil de colorear. 
    La imagen NO debe tener muchos detalles y debe ser fácil de entender.
    La imagen NO contendra texto. La imagen NO estará coloreada. La imagen NO estará dividida en secciones.
    La imagen debe estar relacionada o inspirada en la siguiente frase perteneciente a la historia:
    """
    return base_prompt_template

def base_prompt_to_produce_image_prompt(text:str, number_of_pages:int,):
    base_prompt_template = f"""
    Eres un experto ilustrador de cuentos infantiles. Tu propósito es ilustrar la historia que se te presenta.
    La historia tendrá {number_of_pages-1} imágenes. Cáda imagen debe estar relacionada con el texto de la página.
    Y la vez ser consitente con el argumento de la historia. Las imágenes deben ser sencillas y fáciles de entender.
    Cáda página debe tener una imagen a excepción de la última página. La última página no tendrá imagen.
    Las imágenes deben ser de lineas simples y fáciles de colorear. Las imágenes deben ser originales y creativas.
    El cuento sobre el que basarás las imágenes es el siguiente:
    {text}
    
    En un primer paso razonarás como deben de ser las imágenes para cada página y tu razonamiento será paso a paso.
    Después descrinirás las imágenes que dibujarás para cada página.
    Por último proporcinarás el prompt adecuado para que una IA pueda dibujar las imágenes atendiendo a las especificaciones
    que has dado. Es importante que el prompt sea claro, conciso y que mantenga la coherencia con el texto y las diferentes imágenes.
    Recuerda que las imágenes deben ser fáciles de colorear y de entender, por lo que el prompt debe mencionar que se trata de una imagen
    para colorear y que debe ser sencilla y fácil de entender.
    """
    return base_prompt_template

def generate_base_prompt() -> str:
    """
    Generate a prompt for the story generator
    """
    base_dict_values = history_base_values()
    prompts = []
    for i, name in enumerate(base_dict_values["names"]):
        prompt = base_prompt_template(child_name=name,
                                      number_of_years_child=base_dict_values["number_of_years"][i], 
                                      topic=random.choice(base_dict_values["topics"]),
                                      include_moral_values=base_dict_values["include_moral_values"],
                                      moral_value=random.choice(base_dict_values["moral_values"]),
                                      story_genere=random.choice(base_dict_values["story_genere"]),
                                      language=base_dict_values["language"],
                                      pages=base_dict_values["pages"],
                                      words_per_page=base_dict_values["words_per_page"],
                                      questions=base_dict_values["questions"])
        
        prompts.append(prompt)
    return prompts
def generate_base_prompt_for_chain(number_of_histories:int, base_dict_values:Dict[str,Any]|None = None) -> List[str]:
    """
    Generate a prompt for the story generator
    """
    if base_dict_values is None:
        base_dict_values = history_base_values()
    prompts = []
    for i, name in enumerate(base_dict_values["names"]):
        prompt = base_prompt_template_for_chain(child_name=name,
                                      number_of_years_child=base_dict_values["number_of_years"][i], 
                                      topic=random.choice(base_dict_values["topics"]),
                                      include_moral_values=base_dict_values["include_moral_values"],
                                      moral_value=random.choice(base_dict_values["moral_values"]),
                                      story_genere=random.choice(base_dict_values["story_genere"]),
                                      language=base_dict_values["language"],
                                      pages=base_dict_values["pages"],
                                      words_per_page=base_dict_values["words_per_page"],
                                      number_of_histories=number_of_histories)
        
        prompts.append(prompt)
    return prompts
def generate_base_prompt_review(data:Dict[str,str],
                                base_dict_values:Dict[str,Any]|None = None,
                                other_histories:str|None = None) -> List[str]:
    """
    Generate a prompt for the review story generator
    """
    if base_dict_values is None:
        base_dict_values = history_base_values()
    prompts = []
    for i, (k, text) in enumerate(data.items()):
        prompt = review_best_history_template(text=text,
                                                language=base_dict_values["language"],
                                               number_of_years_child=base_dict_values["number_of_years"][i],
                                               number_of_words=base_dict_values["words_per_page"],
                                               questions=base_dict_values["questions"],
                                               other_histories=other_histories)
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

def generate_base_prompt_to_produce_image_prompt(data:Dict[str,Dict[str,str]]) -> str:
    prompts = []
    for i, (history, k_v) in enumerate(data.items()):
        complete_story = ""
        number_of_pages = 0
        for j, (element, text) in enumerate(k_v.items()):
            if "page" in element:
                complete_story += f"""
                    {element}: {text}

                    """
                number_of_pages += 1
                
        prompt = base_prompt_to_produce_image_prompt(text=complete_story,
                                                        number_of_pages=number_of_pages-2)
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

def prepare_answer_format_for_chain(number_of_histories:int) -> ResponseSchema:
    """
    Prepare the answer format for the story generator
    """
    response_schemas = []
    for i in range(number_of_histories):
        response_schemas.append(ResponseSchema(name=f"history_{i}",
                                               description=f"add text for history {i}"))
    response_schemas.append(ResponseSchema(name="reasoning",
                                             description="add reasoning for the best history"))
    response_schemas.append(ResponseSchema(name="best_history",
                                             description="add the number of the best history",
                                             type="int"))
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser
    
def prepare_answer_format_review(base_dict_values:Dict[str,str]|None = None) -> List[ResponseSchema]:
    """
    Prepare the answer format for the story generator
    """
    if base_dict_values is None:
        base_dict_values = history_base_values()
    number_of_pages = base_dict_values["pages"]
    questions = base_dict_values["questions"]
    response_schemas = [
        ResponseSchema(name="reasoning",
                        description="add reasoning for the reviewed history"),
    ]
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
def prepare_answer_format_to_prompt_image(base_dict_values:Dict[str,Any]|None  = None) -> ResponseSchema:
    """
    Prepare the answer format for the story generator
    """
    if base_dict_values is None:
        base_dict_values = history_base_values()
    number_of_pages = base_dict_values["pages"]
    number_of_images = number_of_pages - 1
    response_schemas = [
        ResponseSchema(name="reasoning",
                        description="add reasoning for the images"),
    ]
    for i in range(number_of_images):
        response_schemas.append(ResponseSchema(name=f"description_image_{i}",
                                               description=f"add text for the description of the image {i} of the story"))
        response_schemas.append(ResponseSchema(name=f"prompt_image_{i}",
                                                  description=f"add prompt for to create the image {i} of the story"))
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    return output_parser

def generate_prompts(base_prompts:List[str]|None = None,
                     output_parser:List[ResponseSchema]|None = None) -> PromptTemplate:
    """
    Prepare the prompt for the story generator
    """
    if base_prompts is None and output_parser is None:
        base_prompts = generate_base_prompt()
        output_parser = prepare_answer_format()

    format_instructions = output_parser.get_format_instructions()
    output_prompts = []
    for base_prompt in base_prompts: 
        prompt = PromptTemplate(
            template=f"{base_prompt} "+"\n{format_instructions}\n{question}",
            input_variables=["question"],
            partial_variables={"format_instructions": format_instructions},
        )
        output_prompts.append(prompt)
    return output_parser, output_prompts

def generate_prompts_for_chain(number_of_histories:int,base_dict_values:Dict[str,Any]|None = None) -> PromptTemplate:
    """
    Prepare the prompt for the story generator
    """
    base_promts = generate_base_prompt_for_chain(number_of_histories, base_dict_values=base_dict_values)
    output_parser = prepare_answer_format_for_chain(number_of_histories)

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
    prompt = generate_prompts_for_chain(4)
    print(prompt[1])