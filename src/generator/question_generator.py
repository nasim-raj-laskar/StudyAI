from src.models.question_schemas import MCQQuestion, FillBlankQuestion
from src.models.summary_schema import SummarySchema
from src.models.flashcard_schema import FlashcardSet
from src.llm.groq_client import get_groq_llm
from src.prompts.templates import (
    mcq_prompt_template, 
    fill_blank_prompt_template,
    summarizer_prompt_template,
    flashcard_prompt_template
)
from src.config.setting import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException


class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)

        # Structured LLMs
        self.mcq_llm = self.llm.with_structured_output(MCQQuestion)
        self.fill_blank_llm = self.llm.with_structured_output(FillBlankQuestion)
        self.summary_llm = self.llm.with_structured_output(SummarySchema)
        self.flashcard_llm = self.llm.with_structured_output(FlashcardSet)

    def _retry_and_generate(self, structured_llm, prompt_template, topic, difficulty):
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic: {topic}, difficulty: {difficulty}, attempt: {attempt + 1}")

                prompt = prompt_template.format(topic=topic, difficulty=difficulty)
                question = structured_llm.invoke(prompt)

                self.logger.info(f"Successfully generated question on attempt {attempt + 1}")
                return question

            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Failed to generate question after {settings.MAX_RETRIES} attempts", e)

    def generate_mcq(self, topic: str, difficulty: str = "medium") -> MCQQuestion:
        try:
            question = self._retry_and_generate(self.mcq_llm,mcq_prompt_template,topic,difficulty)

            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise CustomException("Invalid MCQ format received from LLM")

            self.logger.info("Generated MCQ question successfully")
            return question

        except Exception as e:
            self.logger.error(f"Error generating MCQ question: {str(e)}")
            raise CustomException("Error generating MCQ question", e)

    def generate_fill_blank(self, topic: str, difficulty: str = "medium") -> FillBlankQuestion:
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating fill-blank question, attempt: {attempt + 1}")
                
                prompt = fill_blank_prompt_template.format(topic=topic, difficulty=difficulty)
                question = self.fill_blank_llm.invoke(prompt)

                if question and question.question and question.answer and "_____" in question.question:
                    self.logger.info("Generated Fill-in-the-Blank question successfully")
                    return question
                else:
                    self.logger.warning(f"Invalid format on attempt {attempt + 1}, retrying...")
                    
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                
        raise CustomException("Error generating Fill-in-the-Blank question", None)

    def generate_summary(self, topic: str) -> SummarySchema:
        try:
            self.logger.info(f"Generating summary for content...")
            prompt = summarizer_prompt_template.format(topic=topic)
            summary = self.summary_llm.invoke(prompt)
            self.logger.info("Generated summary successfully")
            return summary
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            raise CustomException("Error generating summary", e)

    def generate_flashcards(self, topic: str, num_cards: int = 5) -> FlashcardSet:
        try:
            self.logger.info(f"Generating {num_cards} flashcards...")
            prompt = flashcard_prompt_template.format(topic=topic, num_cards=num_cards)
            flashcards = self.flashcard_llm.invoke(prompt)
            self.logger.info("Generated flashcards successfully")
            return flashcards
        except Exception as e:
            self.logger.error(f"Error generating flashcards: {str(e)}")
            raise CustomException("Error generating flashcards", e)
