from langchain_core.prompts import PromptTemplate

mcq_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} multiple-choice question about {topic}.\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A clear, specific question\n"
        "- 'options': An array of exactly 4 possible answers\n"
        "- 'correct_answer': One of the options that is the correct answer\n"
        "- 'explanation': A detailed explanation of why the answer is correct\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "What is the capital of France?",\n'
        '    "options": ["London", "Berlin", "Paris", "Madrid"],\n'
        '    "correct_answer": "Paris",\n'
        '    "explanation": "Paris has been the capital of France since the late 10th century and is its most populous city."\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)

fill_blank_prompt_template = PromptTemplate(
    template=(
        "Generate a {difficulty} fill-in-the-blank question about {topic}.\n\n"
        "IMPORTANT: The question MUST contain exactly five underscores in a row: _____\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'question': A sentence with '_____' (5 underscores) marking where the blank should be\n"
        "- 'answer': The correct word or phrase that belongs in the blank\n"
        "- 'explanation': A detailed explanation of why the answer is correct\n\n"
        "Example format:\n"
        '{{\n'
        '    "question": "The capital of France is _____.",\n'
        '    "answer": "Paris",\n'
        '    "explanation": "Paris is the capital city of France, located in the north-central part of the country."\n'
        '}}\n\n'
        "Your response:"
    ),
    input_variables=["topic", "difficulty"]
)

summarizer_prompt_template = PromptTemplate(
    template=(
        "Analyze the following content and provide a concise summary.\n\n"
        "Content: {topic}\n\n"
        "Return ONLY a JSON object with these exact fields:\n"
        "- 'main_idea': The core message of the text\n"
        "- 'key_points': A list of the most important takeaways\n\n"
        "Your response:"
    ),
    input_variables=["topic"]
)

flashcard_prompt_template = PromptTemplate(
    template=(
        "Create {num_cards} study flashcards from the following content.\n\n"
        "Content: {topic}\n\n"
        "Return ONLY a JSON object with a 'flashcards' field containing an array of objects. Each object MUST have:\n"
        "- 'front': A question or concept\n"
        "- 'back': The corresponding answer or explanation\n\n"
        "Your response:"
    ),
    input_variables=["topic", "num_cards"]
)