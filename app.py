import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()

def main():
    st.set_page_config(
        page_icon=":books:",
        layout="wide"
    )
    
    # Custom CSS for Premium Look
    st.markdown("""
    <style>
        .main {
            background-color: #f0f2f6;
        }
        .stButton>button {
            border-radius: 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .config-card {
            padding: 2rem;
            border-radius: 15px;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
            border: 1px solid #e0e6ed;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .config-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px rgba(0,0,0,0.1);
        }
        .section-header {
            color: #1e293b;
            font-weight: 700;
            margin-bottom: 1rem;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 0.5rem;
        }
        /* Center content logic */
        .centered-container {
            max-width: 800px;
            margin: 0 auto;
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
        
    if not st.session_state.quiz_generated:
        st.markdown('<div class="centered-container">', unsafe_allow_html=True)
        st.title("Study-AI 📚")
        st.write("### Prepare your ultimate study materials in seconds.")
        
        # Grid Layout for Settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="config-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">⚙️ Quiz Settings</div>', unsafe_allow_html=True)
            question_type = st.selectbox(
                "Select Question Type",
                ["Multiple Choice", "Fill in the Blank"]
            )
            num_questions = st.slider("Number of Quiz Questions", 1, 25, 5)
            difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="config-card">', unsafe_allow_html=True)
            st.markdown('<div class="section-header">🗂️ Study Aids</div>', unsafe_allow_html=True)
            num_flashcards = st.slider("Number of Flashcards", 1, 15, 5)
            st.info("AI Summarizer will automatically process the content for the Summary tab.")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="config-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-header">📂 Content Source</div>', unsafe_allow_html=True)
        content_source = st.radio("Choose how to provide content:", ["Topic", "Text Paste", "PDF Upload"], horizontal=True)
        
        source_content = ""
        if content_source == "Topic":
            topic = st.text_input("Enter Topic", placeholder="e.g., Quantum Physics, Photosynthesis")
            source_content = topic
        elif content_source == "Text Paste":
            source_content = st.text_area("Paste your study notes here...", height=200)
        elif content_source == "PDF Upload":
            pdf_file = st.file_uploader("Upload a PDF document", type=["pdf"])
            if pdf_file:
                extracted_text = extract_text_from_pdf(pdf_file)
                if extracted_text.startswith("Error"):
                    st.error(extracted_text)
                else:
                    source_content = extracted_text
                    st.success("PDF Content Extracted!")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("✨ Generate Study Materials", use_container_width=True):
            if not source_content:
                st.error("Please provide a topic, text, or PDF!")
            else:
                st.session_state.quiz_submitted = False
                with st.status("🚀 Processing with AI...", expanded=True) as status:
                    generator = QuestionGenerator()
                    st.write("Generating Summary...")
                    st.session_state.quiz_manager.generate_summary(generator, source_content[:4000])
                    
                    st.write(f"Creating {num_flashcards} Flashcards...")
                    st.session_state.quiz_manager.generate_flashcards(generator, source_content[:2000], num_flashcards)

                    st.write(f"Crafting {num_questions} Quiz Questions...")
                    progress_bar = st.progress(0)
                    success = st.session_state.quiz_manager.generate_questions(
                        generator, source_content[:2000], question_type, difficulty, num_questions,
                        progress_callback=lambda p: progress_bar.progress(p)
                    )
                    
                    if success:
                        status.update(label="All set! Your materials are ready.", state="complete", expanded=False)
                        st.session_state.quiz_generated = True
                        rerun()
                    else:
                        status.update(label="Something went wrong during generation.", state="error")
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Results View (already has tabs)
        st.sidebar.button("🔄 Start New Session", on_click=lambda: st.session_state.update({"quiz_generated": False, "quiz_submitted": False}))
        st.sidebar.header("Global Controls")
        # Existing tab logic below...
        
    if st.session_state.quiz_generated:
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🗂️ Flashcards", "❓ Quiz"])

        with tab1:
            if st.session_state.quiz_manager.summary:
                st.header("Content Summary")
                st.subheader(st.session_state.quiz_manager.summary.main_idea)
                st.write("### Key Points")
                for point in st.session_state.quiz_manager.summary.key_points:
                    st.write(f"- {point}")
            else:
                st.info("Generating summary...")

        with tab2:
            if st.session_state.quiz_manager.flashcards:
                st.header("Automated Flashcards")
                for i, card in enumerate(st.session_state.quiz_manager.flashcards):
                    with st.expander(f"Flashcard {i+1}: {card.front}"):
                        st.success(f"**Answer:** {card.back}")
            else:
                st.info("Generating flashcards...")

        with tab3:
            if not st.session_state.quiz_submitted:
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