import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()

def main():
    st.set_page_config(
        page_title="StudyBuddyAI",
        page_icon=":books:",
        layout="wide"
    )
    
    # Custom CSS for Premium Look
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 20px;
            font-weight: 600;
        }
        .result-card {
            padding: 20px;
            border-radius: 15px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
        
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
        
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
        
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False
        
    st.title("StudyBuddyAI 📚")
    
    st.sidebar.header("Quiz Settings")
    
    question_type = st.sidebar.selectbox(
        "Select Question Type",
        ["Multiple Choice", "Fill in the Blank"],
        index=0                                        #by default select Multiple Choice
    )
    num_questions = st.sidebar.slider(
        "Number of Questions",
        min_value=1,
        max_value=25,
        value=5                                              #default 5 questions
    )
    
    difficulty = st.sidebar.selectbox(
        "Select Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1                                     #by default select Medium
    )
    
    st.sidebar.markdown("---")
    content_source = st.sidebar.radio("Content Source", ["Topic", "Text Paste", "PDF Upload"])
    
    source_content = ""
    if content_source == "Topic":
        topic = st.sidebar.text_input("Enter Topic", placeholder="e.g., Python Programming")
        source_content = topic
    elif content_source == "Text Paste":
        source_content = st.sidebar.text_area("Paste Text Content", height=200)
    elif content_source == "PDF Upload":
        pdf_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])
        if pdf_file:
            source_content = extract_text_from_pdf(pdf_file)
            st.sidebar.success("PDF Content Extracted!")

    if st.sidebar.button("Generate Quiz"):
        if not source_content:
            st.sidebar.error("Please provide content source!")
        else:
            st.session_state.quiz_submitted = False
            
            with st.status("Generating your quiz...", expanded=True) as status:
                st.write("Initializing AI generator...")
                generator = QuestionGenerator()
                
                st.write(f"Creating {num_questions} questions for your content...")
                progress_bar = st.progress(0)
                
                # We need to modify generate_questions to support progress callbacks or just do it here
                # For simplicity, if we want a real progress bar, we might need to change helpers.py
                # But let's at least show the status.
                
                success = st.session_state.quiz_manager.generate_questions(
                    generator,
                    source_content[:2000],
                    question_type,
                    difficulty,
                    num_questions,
                    progress_callback=lambda p: progress_bar.progress(p)
                )
                
                if success:
                    status.update(label="Quiz generated successfully!", state="complete", expanded=False)
                else:
                    status.update(label="Failed to generate quiz.", state="error")
                    
            st.session_state.quiz_generated = success 
            rerun()
        
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions and not st.session_state.quiz_submitted:
        st.header("Quiz") 
        st.session_state.quiz_manager.attempt_quiz()
        
        if st.button("Submit Answers"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()
    
    if st.session_state.quiz_submitted:
        st.header("Quiz Results 📊")
        results_df=st.session_state.quiz_manager.get_results_dataframe()
        
        if not results_df.empty:
            correct_count=results_df["is_correct"].sum()
            total_questions=len(results_df)
            score_percentage=(correct_count/total_questions)*100
            
            # Premium Score Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Correct Answers", f"{correct_count}/{total_questions}")
            col2.metric("Score Percentage", f"{score_percentage:.1f}%")
            col3.metric("Status", "Passed ✅" if score_percentage >= 50 else "Keep Studying! 📚")

            # Performance Chart
            st.write("### Performance Breakdown")
            chart_data = pd.DataFrame({
                "Result": ["Correct", "Incorrect"],
                "Count": [correct_count, total_questions - correct_count]
            })
            st.bar_chart(chart_data, x="Result", y="Count", color="#4CAF50")

            if score_percentage == 100:
                st.balloons()
                st.success("Perfect Score! You're a Genius! 🌟")
            
            st.markdown("---")
            
            # Result List with Expanders
            for _, result in results_df.iterrows():
                question_num=result['question_number']
                
                with st.container():
                    if result['is_correct']:
                        st.markdown(f"**Question {question_num}**: {result['question']} ✅")
                    else:
                        st.markdown(f"**Question {question_num}**: {result['question']} ❌")
                        st.write(f"Your Answer: `{result['user_answer']}`")
                        st.write(f"Correct Answer: `{result['correct_answer']}`")
                    
                    with st.expander("Show AI Explanation"):
                        st.info(result['explanation'])
                    
                st.markdown("---")
                
            if st.button("Save Results"):
                saved_file=st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file, "rb") as f:
                        st.download_button(
                            label="Download Results CSV",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime="text/csv"
                        )
                else:
                    st.warning("No results to display.")
                
if __name__ == "__main__":
    main()