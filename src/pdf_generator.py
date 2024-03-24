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

def add_image(doc,image_str, image_path:str, width:str= '0.75')->None:
        image_path = str(image_path.resolve())   
        hf.convert_base64_to_jpg(image_str, image_path)
        with doc.create(Figure(position='h!')) as figure:
            figure.add_image(image_path, width=NoEscape( rf'{width}\textwidth'))
        #hf.delete_image(image_path)
def set_up_document(path:str, type:str = 'article',points:str = '16pt')->Document:
    doc = Document(default_filepath = path,
        documentclass=type,
        page_numbers=False,
        document_options=[points])
    return doc
def set_up_title(doc, title:str)->None:
    doc.preamble.append(Command('title', title))
    doc.preamble.append(NoEscape(r'\usepackage{titling}'))
    doc.preamble.append(NoEscape(r'\pretitle{\begin{center}\Huge\bfseries}'))
    doc.preamble.append(NoEscape(r'\posttitle{\end{center}}'))
    doc.preamble.append(Command('date', '')) 
    doc.append(NoEscape(r'\maketitle'))

def set_up_first_page(data:Dict[str, Dict[str, str]], path:str, title:str, history:str, width:str = '0.75'):
    doc = set_up_document(path, type='article', points='16pt')
    
    set_up_title(doc, title)
    image_path = Path(__file__).parent.parent /"images" / "temp_image_0.jpg"
    if "image_0" in data[history].keys(): 
        image_src = data[history]['image_0']
        add_image(doc, image_src, image_path, width=width)
    if "page_0" in data[history].keys():
        doc.append(NoEscape(r'\Huge'))
        doc.append(NoEscape(data[history]['page_0']))
    return doc
def set_up_middle_page(data:Dict[str, Dict[str, str]], path:str,doc:str|None, history:str, image_key:str, current_page:str, width:str = '0.75')->Document:
    if doc is None:
        doc = set_up_document(path, type='article', points='16pt')
    if image_key in data[history].keys():
        image_path = Path(__file__).parent.parent /"images" / f"temp_{image_key}.jpg"
        image_url = data[history][image_key]
        add_image(doc,image_url, image_path,width=width)
    doc.append(NoEscape(r'\Huge'))    
    if current_page in data[history].keys():
        doc.append(NoEscape(data[history][current_page]))
    return doc

def number_of_pages_in_first_page(data:Dict[str, Dict[str, str]], path:str, title:str, history:str, width:str = '0.75')->str:
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
def number_of_pages_in_middle_page(data:Dict[str, Dict[str, str]], path:str,
                                   history:str, image_key:str, current_page:str,
                                   width:str = '0.75',
                                   )->str:
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
    

def generate_pdf(data:Dict[str, Dict[str, str]], test_mode:bool = False)->None:
    base_dict_values = history_base_values()
    numeber_of_pages = base_dict_values["pages"]
    number_of_questions = base_dict_values["questions"]

    #language
    reference_languages = ['catalan', 'spanish', 'english', 
                           'french', 'german', 'italian', 'portuguese']
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
                doc = set_up_first_page(data, path, title, history, width)

            elif j !=0 and numeber_of_pages-1 != j:
                doc.append(NewPage())
                image_key = f'image_{j}'
                current_page = f'page_{j}'
                width = number_of_pages_in_middle_page(data = data, path = path_moke, history=history, image_key= image_key, current_page=current_page, width= '0.75')
                doc = set_up_middle_page(data = data, path = path_moke, doc = doc, history= history, image_key = image_key, current_page = current_page , width= width)
            else:
                doc.append(NewPage())
                current_page = f'page_{j}'
                if current_page in data[history].keys():
                    doc.append(NoEscape(r'\Huge'))
                    doc.append(NoEscape(data[history][current_page]))
                if number_of_questions > 0:
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


        doc.generate_pdf(clean_tex=True, compiler='pdflatex')
        # sleep 1 second to avoid errors
        time.sleep(1)

            
    


if __name__ == '__main__':
    with open(r'C:\proyectos_personales\Cuentos\out_put_test\2024-03-24_18-35-14_history_images.pkl', 'rb') as f:
        data = pickle.load(f)
    generate_pdf(data, test_mode=True)
    print("Done!")
