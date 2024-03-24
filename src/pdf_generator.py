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

def generate_pdf(data:Dict[str, Dict[str, str]]):
    base_dict_values = history_base_values()
    numeber_of_pages = base_dict_values["pages"]
    number_of_questions = base_dict_values["questions"]

    #language
    reference_languages = ['catalan', 'spanish', 'english', 
                           'french', 'german', 'italian', 'portuguese']
    language = base_dict_values["language"].lower()
    if language not in reference_languages:
        language = hf.calculate_levenshtein_distance(reference_languages, language)

    len_data = len(data)
    for i, (history, details) in enumerate(data.items()):
        for j in range(numeber_of_pages):

            if j == 0:

                now = dt.now().strftime("%Y-%m-%d_%H-%M-%S")

                path = Path(__file__).parent.parent / "data" 

                path = Path.joinpath(path, f'{now}_histories')

                doc = Document(default_filepath = path,
                        documentclass='article',
                        page_numbers=False,
                        document_options=['16pt'])
                title = data[history]["title"]
                doc.preamble.append(Command('title', title))
                doc.preamble.append(NoEscape(r'\usepackage{titling}'))
                doc.preamble.append(NoEscape(r'\pretitle{\begin{center}\Huge\bfseries}'))
                doc.preamble.append(NoEscape(r'\posttitle{\end{center}}'))
                doc.preamble.append(Command('date', '')) 
                doc.append(NoEscape(r'\maketitle'))
                image_path = Path(__file__).parent.parent /"images" / "temp.jpg"
                if "image_0" in data[history].keys(): 
                    image_src = data[history]['image_0']
                    add_image(doc, image_src, image_path)
                if "page_0" in data[history].keys():
                    doc.append(NoEscape(r'\Huge'))
                    doc.append(NoEscape(data[history]['page_0']))
            elif j !=0 and len_data-1 != j:
                doc.append(NewPage())
                image_key = f'image_{j}'
                if image_key in data[history].keys():
                    image_url = data[history][image_key]
                    add_image(doc,image_url, image_path)
                doc.append(NoEscape(r'\Huge'))
                current_page = f'page_{j}'
                if current_page in data[history].keys():
                    doc.append(NoEscape(data[history][current_page]))
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
    with open(r'C:\proyectos_personales\Cuentos\data\2024-03-24_11-58-45_histories_images.pkl', 'rb') as f:
        data = pickle.load(f)
    generate_pdf(data)
    # print(data['history_0'].keys())
    # print(data['history_0']['page_1'])

    print("Done!")
    # path = r'C:\proyectos_personales\Cuentos\data\2024-03-24_11-58-45_histories.pkl'
    # with open(path, 'rb') as f:
    #     data = pickle.load(f)
    # print(data['history_0'])