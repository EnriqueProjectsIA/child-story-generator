import pickle
import helper_functions as hf
from pylatex import Document, Command, NoEscape, Figure, NewPage
from pylatex.utils import bold
from prepare_prompt import history_base_values
from pathlib import Path
from datetime import datetime as dt
import pickle
from typing import List, Dict
import time
import logging

def add_image(doc, image_str, image_path: str, width: str = '0.75') -> None:
    """
    Add an image to the PDF document.

    Args:
        doc (Document): The PDF document to add the image to.
        image_str (str): The image data in base64 format.
        image_path (str): The path to save the image file.
        width (str, optional): The width of the image in the document. Defaults to '0.75'.

    Returns:
        None
    """
    image_path = str(image_path.resolve())   
    hf.convert_base64_to_jpg(image_str, image_path)
    with doc.create(Figure(position='h!')) as figure:
        figure.add_image(image_path, width=NoEscape(rf'{width}\textwidth'))
    #hf.delete_image(image_path)
def set_up_document(path:str, type:str = 'article',points:str = '16pt')->Document:
    """
    Sets up a document with the specified path, type, and font size.

    Args:
        path (str): The filepath for the document.
        type (str, optional): The type of document. Defaults to 'article'.
        points (str, optional): The font size in points. Defaults to '16pt'.

    Returns:
        Document: The initialized document object.
    """
    doc = Document(default_filepath = path,
        documentclass=type,
        page_numbers=False,
        document_options=[points])
    return doc
def set_up_title(doc, title:str)->None:
    """
    Sets up the title for the document.

    Args:
        doc: The document object.
        title: The title of the document.

    Returns:
        None
    """
    doc.preamble.append(Command('title', title))
    doc.preamble.append(NoEscape(r'\usepackage{titling}'))
    doc.preamble.append(NoEscape(r'\pretitle{\begin{center}\Huge\bfseries}'))
    doc.preamble.append(NoEscape(r'\posttitle{\end{center}}'))
    doc.preamble.append(Command('date', '')) 
    doc.append(NoEscape(r'\maketitle'))


def set_up_first_page(data: Dict[str, Dict[str, str]], path: str, title: str, history: str, width: str = '0.75'):
    """
    Set up the first page of the document.

    Args:
        data (Dict[str, Dict[str, str]]): A dictionary containing data for the document.
        path (str): The path to save the document.
        title (str): The title of the document.
        history (str): The history key to retrieve data from.
        width (str, optional): The width of the image. Defaults to '0.75'.

    Returns:
        doc: The configured document object.
    """
    doc = set_up_document(path, type='article', points='16pt')
    
    set_up_title(doc, title)
    image_path = Path(__file__).parent.parent / "images" / "temp_image_0.jpg"
    if "image_0" in data[history].keys(): 
        image_src = data[history]['image_0']
        add_image(doc, image_src, image_path, width=width)
    if "page_0" in data[history].keys():
        doc.append(NoEscape(r'\Huge'))
        doc.append(NoEscape(data[history]['page_0']))
    return doc

def set_up_middle_page(data: Dict[str, Dict[str, str]], path: str, doc: str | None, history: str, image_key: str, current_page: str, width: str = '0.75') -> Document:
    """
    Set up the middle page of the document.

    Args:
        data (Dict[str, Dict[str, str]]): A dictionary containing data.
        path (str): The path of the document.
        doc (str | None): The document object. If None, a new document will be created.
        history (str): The history key.
        image_key (str): The image key.
        current_page (str): The current page key.
        width (str, optional): The width of the image. Defaults to '0.75'.

    Returns:
        Document: The modified document object.
    """
    if doc is None:
        doc = set_up_document(path, type='article', points='16pt')
    
    if image_key in data[history].keys():
        image_path = Path(__file__).parent.parent / "images" / f"temp_{image_key}.jpg"
        image_url = data[history][image_key]
        add_image(doc, image_url, image_path, width=width)
    
    doc.append(NoEscape(r'\Huge'))
    
    if current_page in data[history].keys():
        doc.append(NoEscape(data[history][current_page]))
    
    return doc


def number_of_pages_in_first_page(data: Dict[str, Dict[str, str]], path: str, title: str, history: str, width: str = '0.75') -> str:
    """
    Calculates the number of pages in the first page of a PDF document.
    The function adjusts the width of the first page to fit the content.
    Args:
        data (Dict[str, Dict[str, str]]): A dictionary containing data for the PDF document.
        path (str): The path where the PDF document will be saved.
        title (str): The title of the PDF document.
        history (str): The history of the PDF document.
        width (str, optional): The width of the first page. Defaults to '0.75'.

    Returns:
        str: The updated width of the first page.

    """
    for _ in range(5):
        doc = set_up_first_page(data, path, title, history, width)
        doc.generate_pdf(clean_tex=True, compiler='pdflatex')
        count_path = Path(path).with_suffix('.pdf')
        number_of_pages = hf.count_number_of_pages(count_path)
        if number_of_pages > 1:
            width = str(float(width) - 0.05)
            count_path.unlink()
        else:
            count_path.unlink()
            return width

def number_of_pages_in_middle_page(data: Dict[str, Dict[str, str]], path: str,
                                   history: str, image_key: str, current_page: str,
                                   width: str = '0.75') -> str:
    """
    Calculates the number of pages in the middle page of a PDF document.
    The function adjusts the width of the middle page to fit the content.
    Args:
        data (Dict[str, Dict[str, str]]): A dictionary containing data.
        path (str): The path to the PDF document.
        history (str): The history of the document.
        image_key (str): The key for the image.
        current_page (str): The current page of the document.
        width (str, optional): The width of the page. Defaults to '0.75'.

    Returns:
        str: The updated width of the page.

    """
    for _ in range(5):
        doc = set_up_middle_page(data, path, None, history, image_key, current_page, width)
        doc.generate_pdf(clean_tex=True, compiler='pdflatex')
        count_path = Path(path).with_suffix('.pdf')
        number_of_pages = hf.count_number_of_pages(count_path)
        if number_of_pages > 1:
            width = str(float(width) - 0.05)
            count_path.unlink()
        else:
            count_path.unlink()
            return width
    


def generate_pdf(data: Dict[str, Dict[str, str]], test_mode: bool = False, logger:logging.Logger|None = None ) -> None:
    """
    Generate a PDF document based on the provided data.

    Args:
        data (Dict[str, Dict[str, str]]): A dictionary containing the data for generating the PDF.
            The keys represent the history names, and the values are dictionaries containing the
            details for each history.
        test_mode (bool, optional): A flag indicating whether the PDF should be generated in test mode.
            Defaults to False.

    Returns:
        None
    """
    base_dict_values = history_base_values()
    numeber_of_pages = base_dict_values["pages"]
    number_of_questions = base_dict_values["questions"]

    #language
    reference_languages = ['catalan', 'spanish', 'english', 'french', 'german', 'italian', 'portuguese']
    language = base_dict_values["language"].lower()
    if language not in reference_languages:
        language = hf.calculate_levenshtein_distance(reference_languages, language)

    for i, (history, details) in enumerate(data.items()):
        for j in range(numeber_of_pages):

            if j == 0:
                now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

                if test_mode:
                    path = Path(__file__).parent.parent / "out_put_test"
                    path_moke = Path(__file__).parent.parent / "out_put_test"
                else:
                    path = Path(__file__).parent.parent / "data"
                    path_moke = Path(__file__).parent.parent / "data"

                path = Path.joinpath(path, f'{now}_histories')
                path_moke = Path.joinpath(path_moke, f'moke_page')
                title = data[history]["title"]
                width = number_of_pages_in_first_page(data, path, title, history)
                if logger is not None:
                    logger.info(f"The width of the first page is {width}")
                doc = set_up_first_page(data, path, title, history, width)

            elif j !=0 and numeber_of_pages-1 != j:
                doc.append(NewPage())
                image_key = f'image_{j}'
                current_page = f'page_{j}'
                width = number_of_pages_in_middle_page(data = data, path = path_moke,
                                                       history=history, image_key= image_key,
                                                       current_page=current_page, width= '0.75')
                if logger is not None:
                    logger.info(f"The width of the page {j} is {width}")
                doc = set_up_middle_page(data = data, path = path_moke, 
                                         doc = doc, history= history, 
                                         image_key = image_key, 
                                         current_page = current_page , width= width)
            else:
                doc.append(NewPage())
                current_page = f'page_{j}'
                if current_page in data[history].keys():
                    doc.append(NoEscape(r'\Huge'))
                    doc.append(NoEscape(data[history][current_page]))
                if number_of_questions > 0:
                    if logger is not None:
                        logger.info(f"Adding {number_of_questions} questions to the document {history}")
                    for k in range(number_of_questions):
                        question = f'question_{k}'
                        if question in data[history].keys():
                            doc.append(NoEscape(r'\newline'))
                            doc.append(NoEscape(r'\newline'))
                            doc.append(NoEscape(r'\Huge'))
                            doc.append(NoEscape(data[history][question]))
                            # add underline for the answer
                            doc.append(NoEscape(r'\newline'))
                            doc.append(NoEscape(r'\underline{\hspace{10cm}}'))
                            if logger is not None:
                                logger.info(f"Added question {k} to the document {history}")
        try:
            doc.generate_pdf(clean_tex=True, compiler='pdflatex')
            if logger is not None:
                logger.info(f"Generated PDF for history {history}")
        except Exception as e:
            if logger is not None:
                logger.error(f"Error generating PDF for history {history}: {e}")
            raise Exception(f"Error generating PDF for history {history}: {e}")
        # sleep 1 second to avoid errors
        time.sleep(1)

            
    


if __name__ == '__main__':
    with open(r'C:\proyectos_personales\Cuentos\out_put_test\2024-03-24_18-35-14_history_images.pkl', 'rb') as f:
        data = pickle.load(f)
    generate_pdf(data, test_mode=True)
    print("Done!")
