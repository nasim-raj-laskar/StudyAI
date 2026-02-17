import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()

def main():
    st.set_page_config(
        page_title="Study-AI",
        page_icon=":books:",
        layout="wide"
    )
    
    # State Initialization
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'source_content' not in st.session_state:
        st.session_state.source_content = ""

    # CSS Injection (Simplified for Maximum Compatibility)
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        body, .main {
            font-family: 'Outfit', sans-serif;
        }
        
        .section-header {
            color: #2563eb;
            font-size: 1.5rem;
            font-weight: 700;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2563eb;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .stButton>button {
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
        }

        .centered-container {
            max-width: 850px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        .step-indicator {
            display: flex;
            justify-content: space-between;
            margin-bottom: 2rem;
            padding: 0.5rem;
            background: rgba(0,0,0,0.05);
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main Content Area
    st.markdown('<div class="centered-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.title("Study-AI 📚")
    with col2:
        if st.session_state.quiz_generated:
            if st.button("🔄 New Session", use_container_width=True, key="new_session_main"):
                st.session_state.update({"quiz_generated": False, "quiz_submitted": False, "step": 1, "source_content": ""})
                st.rerun()
    st.markdown("---")
    
    if not st.session_state.quiz_generated:
        # Step Indicator
        cols = st.columns(3)
        steps = ["1. Content", "2. Config", "3. Study"]
        for i, step_name in enumerate(steps):
            is_active = st.session_state.step == i + 1
            label = f"{step_name}" if is_active else step_name
            cols[i].write(f"<div style='text-align: center; border-bottom: {is_active and '3px solid #2563eb' or '1px solid #ccc'}; padding: 5px;'>{label}</div>", unsafe_allow_html=True)
        
        st.write("")

        if st.session_state.step == 1:
            st.markdown('<div class="section-header">📂 Step 1: Content Source</div>', unsafe_allow_html=True)
            
            source_type = st.radio(
                "How would you like to provide content?", 
                ["Topic", "Text Paste", "PDF Upload"], 
                horizontal=True,
                key="source_type_radio"
            )
            
            if source_type == "Topic":
                topic = st.text_input("Enter Topic", placeholder="e.g., Photosynthesis", key="topic_input")
                st.session_state.source_content = topic
            elif source_type == "Text Paste":
                content = st.text_area("Paste your notes...", height=250, key="text_area_input")
                st.session_state.source_content = content
            elif source_type == "PDF Upload":
                pdf = st.file_uploader("Upload PDF", type=["pdf"], key="pdf_uploader")
                if pdf:
                    text = extract_text_from_pdf(pdf)
                    if text.startswith("Error"):
                        st.error(text)
                    else:
                        st.session_state.source_content = text
                        st.success("PDF Extracted!")
            
            st.write("")
            if st.button("Continue to Setup ➡️", use_container_width=True, key="continue_btn"):
                if not st.session_state.source_content:
                    st.error("Please provide content!")
                else:
                    st.session_state.step = 2
                    st.rerun()

        elif st.session_state.step == 2:
            st.markdown('<div class="section-header">⚙️ Step 2: Configure Session</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                q_type = st.selectbox("Question Type", ["Multiple Choice", "Fill in the Blank"], key="q_type_select")
                diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1, key="diff_select")
            with col2:
                n_ques = st.slider("Number of Questions", 1, 20, 5, key="n_ques_slider")
                n_cards = st.slider("Number of Flashcards", 1, 15, 5, key="n_cards_slider")
            
            st.write("")
            c1, c2 = st.columns(2)
            if c1.button("⬅️ Back", use_container_width=True, key="back_btn"):
                st.session_state.step = 1
                st.rerun()
            if c2.button("✨ Generate Materials", use_container_width=True, key="gen_btn"):
                with st.status("🚀 Processing...", expanded=True) as status:
                    generator = QuestionGenerator()
                    st.write("Generating Summary...")
                    st.session_state.quiz_manager.generate_summary(generator, st.session_state.source_content[:4000])
                    st.write("Creating Flashcards...")
                    st.session_state.quiz_manager.generate_flashcards(generator, st.session_state.source_content[:2000], n_cards)
                    st.write("Crafting Quiz...")
                    success = st.session_state.quiz_manager.generate_questions(
                        generator, st.session_state.source_content[:2000], q_type, diff, n_ques,
                        progress_callback=lambda p: None
                    )
                    if success:
                        status.update(label="Ready!", state="complete")
                        st.session_state.quiz_generated = True
                        st.rerun()
                    else:
                        status.update(label="Error!", state="error")
    
    else:
        # Results View
        tab1, tab2, tab3 = st.tabs(["📝 Summary", "🗂️ Flashcards", "❓ Quiz"])
        
        with tab1:
            if st.session_state.quiz_manager.summary:
                st.header("Content Summary")
                st.subheader(st.session_state.quiz_manager.summary.main_idea)
                for point in st.session_state.quiz_manager.summary.key_points:
                    st.markdown(f"- {point}")
                    
        with tab2:
            if st.session_state.quiz_manager.flashcards:
                st.header("Flashcards")
                for i, card in enumerate(st.session_state.quiz_manager.flashcards):
                    with st.expander(f"Card {i+1}: {card.front}"):
                        st.info(f"Answer: {card.back}")
                        
        with tab3:
            if not st.session_state.quiz_submitted:
                st.header("Take the Quiz")
                st.session_state.quiz_manager.attempt_quiz()
                if st.button("Submit", key="quiz_submit_btn"):
                    st.session_state.quiz_manager.evaluate_quiz()
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                st.header("Results 📊")
                results_df = st.session_state.quiz_manager.get_results_dataframe()
                if not results_df.empty:
                    correct = results_df["is_correct"].sum()
                    total = len(results_df)
                    st.metric("Score", f"{correct}/{total}", delta=f"{(correct/total)*100:.0f}%")
                    
                    for _, row in results_df.iterrows():
                        icon = "✅" if row['is_correct'] else "❌"
                        with st.container():
                            st.markdown(f"**Q{row['question_number']}**: {row['question']} {icon}")
                            if not row['is_correct']:
                                st.write(f"Yours: {row['user_answer']} | Correct: {row['correct_answer']}")
                            with st.expander("Why?"):
                                st.write(row['explanation'])
    
    st.markdown('</div>', unsafe_allow_html=True)
                
if __name__ == "__main__":
    main()