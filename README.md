
# Project Cuentos

## Overview
This project uses LLMs to generate personalized child stories and accompanying images. The stories are created based on parameters such as age, theme, and moral values, using OpenAI's GPT model. The images are generated using the DALL-E model.

## Installation and Setup

1. Clone the repository.
2. Navigate to the root directory.
3. Create a virtual environment:
   ```sh
   python -m venv my_env
   ```
4. Activate the virtual environment:
   - Windows: `my_env\Scripts\activate`
   - Unix/MacOS: `source my_env/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`

## Configuration

1. Create a `.env` file with your OpenAI API key: `OPENAI_API_KEY`.


## Configuration

The `configuration.ini` file is used to set up the parameters for the story generation. Here's an overview of its sections and settings:

- `[childs]`: Define the names and birthdays of the children for whom the stories are generated. There must be a birthday corresponding to each name.
  - `NAMES`: Comma-separated list of names.
  - `BIRTHDAYS`: Comma-separated list of birth dates in `YYYY-MM-DD` format.

- `[history]`: Parameters for the story topics, moral values, and genre are selected at random to produce unique stories.
  - `TOPICS`: Comma-separated list of potential topics for the stories.
  - `MORAL_VALUES`: Comma-separated list of moral values to be included in the stories.
  - `STORY_GENERE`: Comma-separated list of story genres.

- `[book]`: Defines the language of the story, the number of pages, and the word count per page. Note that the number of images generated will be one less than the number of pages.
  - `LANGUAGE`: Language of the book. Recommended languages for proper LaTeX compilation include 'catalan', 'spanish', 'english', 'french', 'german', 'italian', 'portuguese'.
  - `PAGES`: Total number of pages in the story.
  - `WORDS_PER_PAGE`: The maximum number of words per page.

- `[activity]`: Configures the number of comprehension questions to follow each story, which help promote understanding.
  - `QUESTIONS`: Number of questions to be generated; if set to zero, no questions will be generated.

Ensure to fill in these details as needed for the stories to be generated appropriately.


## Usage

Run `main.py` to start the story, image generation, and PDF creation process.

## Scripts

- `history_generator.py`: Generates stories.
- `image_generator.py`: Generates images for stories.
- `pdf_generator.py`: Compiles stories and images into a PDF.

## Project Structure

```plaintext
Folder/
├── my_env/
├── data/
├── images/
├── out_put_test/
├── src/
│   ├── __pycache__/
│   ├── helper_functions.py
│   ├── history_generator.py
│   ├── image_generator.py
│   ├── pdf_generator.py
│   └── prepare_prompt.py
├── .env
├── .gitignore
├── configuration.ini
├── main.py
├── requirements.txt
└── test_main.py
```

