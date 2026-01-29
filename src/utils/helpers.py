import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator

def rerun():
    st.session_state['rerun_trigger']=not st.session_state.get('rerun_trigger', False)
    
    
class QuizManager:
    def __init__(self):
        self.questions=[]
        self.user_answers=[]
        self.results=[]
        
    def generate_questions(self,generator:QuestionGenerator,topic:str,question_type:str,difficulty:str,num_questions:int):
        self.questions=[]
        self.user_answers=[]
        self.results=[]
        
        try:
            for _ in range(num_questions):
                if question_type=="Multiple Choice":
                    question=generator.generate_mcq(topic, difficulty.lower())
                    
                    self.questions.append({
                        'type':'MCQ',
                        'question':question.question,
                        'options':question.options,
                        'correct_answer':question.correct_answer
                    })
                else:
                    question=generator.generate_fill_blank(topic, difficulty.lower())
                    
                    self.questions.append({
                        'type':'Fill in the Blank',
                        'question':question.question,
                        'correct_answer':question.answer
                    })
                    
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False
        
        return True
                    
    def attempt_quiz(self):
        self.user_answers = []
        for i,q in enumerate(self.questions):
            st.markdown(f"**Question {i+1}: {q['question']}**")
            
            if q['type']=='MCQ':
                user_answer=st.radio(
                    f"Select an option:{i+1}", 
                    q['options'],
                    key=f"mcq_{i}")
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
                result_dict['correct_answer']=q['options']
                result_dict['is_correct']=user_answer==q['correct_answer']
            else:
                result_dict['options']=[]
                result_dict['is_correct']=user_answer.strip().lower()==q['correct_answer'].strip().lower()
                
                
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