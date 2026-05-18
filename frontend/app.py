import streamlit as st
import httpx

# Set up the page layout and title
st.set_page_config(page_title="AI Interview Analyzer", layout="centered")
st.title("🎙️ Autonomous AI Interviewer")
st.caption("Powered by FastAPI, SQLAlchemy, and Llama 3.3 via Groq")

# Define our backend API Base URL
BACKEND_URL = "http://127.0.0.1:8000/api/v1"

# Initialize Session State variables so Streamlit remembers variables across rerenders
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "current_question_id" not in st.session_state:
    st.session_state.current_question_id = None
if "current_question_text" not in st.session_state:
    st.session_state.current_question_text = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "interview_complete" not in st.session_state:
    st.session_state.interview_complete = False

# --- STAGE 1: START THE INTERVIEW ---
if st.session_state.session_id is None:
    st.subheader("Configure Your Mock Interview")
    
    # Updated to use placeholders instead of hardcoded values
    role = st.text_input("Target Job Role", value="", placeholder="e.g., Python Backend Engineer")
    
    # Updated to default to "Select..."
    experience = st.selectbox("Experience Level", ["Select...", "Intern", "Junior", "Mid-Level", "Senior", "Lead"])
    
    # Updated to use placeholders
    tech_stack = st.text_input("Tech Stack (comma separated)", value="", placeholder="e.g., Python, FastAPI, PostgreSQL")

    if st.button("Start Interview", type="primary"):
        # Validation check: Ensure all fields are filled properly
        if not role.strip() or not tech_stack.strip() or experience == "Select...":
            st.warning("⚠️ Please fill all the details before starting the interview!")
        else:
            # Format tech stack into a list
            stack_list = [tech.strip() for tech in tech_stack.split(",") if tech.strip()]
            
            # Call backend to initialize the session
            with st.spinner("Preparing your interview environment..."):
                try:
                    response = httpx.post(
                        f"{BACKEND_URL}/interview/start",
                        json={"role": role, "experience_level": experience, "tech_stack": stack_list},
                        timeout=10.0
                    )
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Use question_id as a fallback session identifier
                        st.session_state.session_id = data.get("session_id") or 1
                        
                        # Match your exact backend response keys
                        st.session_state.current_question_id = data.get("question_id")
                        st.session_state.current_question_text = data.get("text")
                        st.rerun()
                    else:
                        st.error("Failed to start session. Make sure your FastAPI backend is running!")
                except Exception as e:
                    st.error(f"Error connecting to backend: {str(e)}")

# --- STAGE 2: ACTIVE INTERVIEW CHAT ---
elif not st.session_state.interview_complete:
    st.write(f"**Interview Session ID:** {st.session_state.session_id}")
    st.write("---")

    # Display Chat History
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    # Display current question from AI
    with st.chat_message("assistant"):
        st.write(st.session_state.current_question_text)

    # Input form for candidate's answer
    with st.form(key="answer_form", clear_on_submit=True):
        user_answer = st.text_area("Your Answer:", placeholder="Type your technical response here...")
        submit_button = st.form_submit_button(label="Submit Answer", type="primary")

    col1, col2 = st.columns([4, 1])
    with col2:
        finish_button = st.button("Wrap Up & Get Report 📊")

    if submit_button and user_answer:
        # Append answer to historical visual state
        st.session_state.chat_history.append({"role": "assistant", "content": st.session_state.current_question_text})
        st.session_state.chat_history.append({"role": "user", "content": user_answer})

        # Send answer to backend evaluation + get next question
        with st.spinner("AI is evaluating your response and formulating the next question..."):
            try:
                response = httpx.post(
                    f"{BACKEND_URL}/interview/evaluate",
                    json={
                        "question_id": int(st.session_state.current_question_id),
                          "answer_text": str(user_answer),
                          "time_taken_seconds": 0
                          },  
                    timeout=30.0
                )
                if response.status_code == 200:
                    result = response.json()
                    
                    # Extract the nested 'next_question' block safely
                    next_q_data = result.get("next_question", {}) if isinstance(result.get("next_question"), dict) else {}

                    # 1 Safely extract next question ID
                    new_id = next_q_data.get("question_id") or result.get("question_id")
                    if new_id is not None:
                        st.session_state.current_question_id = int(new_id)

                    
                    # 2 Safely extract next question text
                    st.session_state.current_question_text = (
                        next_q_data.get("next_question") or
                        next_q_data.get("text") or
                        result.get("text") or
                        "Great response! Let's move to the next concept. Can you elaborate further?"
                    )
                    st.rerun()
                else:
                    st.error(f"Evaluation failed with status code: {response.status_code}")
            except Exception as e:
                st.error(f"Error evaluating response: {str(e)}")

    if finish_button:
        st.session_state.interview_complete = True
        st.rerun()

# --- STAGE 3: FINAL REPORT DASHBOARD ---
else:
    st.subheader("🏁 Interview Complete! Generating Performance Profile...")
    
    with st.spinner("Compiling database records and conducting Final Manager Review..."):
        try:
            response = httpx.get(f"{BACKEND_URL}/interview/report/{st.session_state.session_id}", timeout=30.0)
            if response.status_code == 200:
                report = response.json()
                
                st.success("Analysis Complete!")
                st.balloons()
                
                # Big Metrics Dashboard
                st.markdown(f"## Final Rating: `{report['final_score']}/10`")
                
                st.markdown("### 📋 Executive Summary")
                st.write(report["summary"])
                
                # Split Columns for Strengths vs Weaknesses
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ Key Strengths")
                    for strength in report["top_strengths"]:
                        st.markdown(f"- {strength}")
                with col2:
                    st.markdown("### ⚠️ Areas for Improvement")
                    for weakness in report["top_weaknesses"]:
                        st.markdown(f"- {weakness}")
                
                st.write("---")
                st.markdown("### 📚 Recommended Actionable Study Topics")
                for topic in report["recommended_study_topics"]:
                    st.markdown(f"- {topic}")
                    
            else:
                st.error("Could not fetch the summary report. Ensure you answered at least one question.")
        except Exception as e:
            st.error(f"Error fetching final report: {str(e)}")
            
    if st.button("Start A New Mock Session"):
        # Reset everything to restart structural workflow
        st.session_state.session_id = None
        st.session_state.current_question_id = None
        st.session_state.current_question_text = None
        st.session_state.chat_history = []
        st.session_state.interview_complete = False
        st.rerun()