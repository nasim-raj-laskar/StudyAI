import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_text_from_pdf(file):
    if PyPDF2 is None:
        return "Error: PyPDF2 library not found. Please install it using 'pip install PyPDF2'."
    
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def rerun():
    st.session_state['rerun_trigger']=not st.session_state.get('rerun_trigger', False)
    
    
class QuizManager:
    def __init__(self):
        self.questions=[]
        self.user_answers=[]
        self.results=[]
        self.summary = None
        self.flashcards = []
        
    def generate_questions(self,generator:QuestionGenerator,topic:str,question_type:str,difficulty:str,num_questions:int, progress_callback=None):
        self.questions=[]
        self.user_answers=[]
        self.results=[]
        
        try:
            for i in range(num_questions):
                if question_type=="Multiple Choice":
                    question=generator.generate_mcq(topic, difficulty.lower())
                    
                    self.questions.append({
                        'type':'MCQ',
                        'question':question.question,
                        'options':question.options,
                        'correct_answer':question.correct_answer,
                        'explanation':question.explanation
                    })
                else:
                    question=generator.generate_fill_blank(topic, difficulty.lower())
                    
                    self.questions.append({
                        'type':'Fill in the Blank',
                        'question':question.question,
                        'correct_answer':question.answer,
                        'explanation':question.explanation
                    })
                
                if progress_callback:
                    progress_callback((i + 1) / num_questions)
                    
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False
        
        return True

    def generate_summary(self, generator: QuestionGenerator, topic: str):
        try:
            self.summary = generator.generate_summary(topic)
            return True
        except Exception as e:
            st.error(f"Error generating summary: {e}")
            return False

    def generate_flashcards(self, generator: QuestionGenerator, topic: str, num_cards: int):
        try:
            flashcard_set = generator.generate_flashcards(topic, num_cards)
            self.flashcards = flashcard_set.flashcards
            return True
        except Exception as e:
            st.error(f"Error generating flashcards: {e}")
            return False
                    
    def attempt_quiz(self):
        self.user_answers = []
        for i,q in enumerate(self.questions):
            st.markdown(f"**Question {i+1}: {q['question']}**")
            
            if q['type']=='MCQ':
                user_answer=st.radio(
                    f"Select an option:", 
                    q['options'],
                    key=f"mcq_{i}",
                    index=None)
                self.user_answers.append(user_answer)
            else:
                user_answer=st.text_input(
                    f"Fill in the blank for Question {i+1}:", 
                    key=f"fill_blank_{i}"
                )
                self.user_answers.append(user_answer)
    
    def evaluate_quiz(self):
        self.results=[]
        
        for i,(q,user_answer) in enumerate(zip(self.questions,self.user_answers)):
            result_dict={
                'question_number':i+1,
                'question':q['question'],
                'question_type':q['type'],
                'user_answer':user_answer,
                'correct_answer':q['correct_answer'],
                'is_correct':False
            }     
            if q['type']=='MCQ':
                result_dict['options']=q['options']
                result_dict['is_correct']=user_answer==q['correct_answer']
            else:
                result_dict['options']=[]
                result_dict['is_correct']=user_answer.strip().lower()==q['correct_answer'].strip().lower()
                
            result_dict['explanation']=q.get('explanation', "No explanation provided.")
                
            self.results.append(result_dict)
            
    def get_results_dataframe(self):
        if not self.results:
            return pd.DataFrame()
        
        return pd.DataFrame(self.results)
    
    def save_to_csv(self,filename_prefix="quiz_results"):
        if not self.results:
            st.warning("No results to save !!")
            return None
        
        df=self.get_results_dataframe()
        
        from datetime import datetime
        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S")
        filename=f"{filename_prefix}_{timestamp}.csv"
        
        os.makedirs('results', exist_ok=True)
        full_path=os.path.join('results', filename)
        
        try:
            df.to_csv(full_path, index=False)
            st.success(f"Results saved to {full_path}")
            return full_path
        except Exception as e:
            st.error(f"Error saving results: {e}")
            return None