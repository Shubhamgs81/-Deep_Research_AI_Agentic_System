import uuid
import traceback
import streamlit as st
from deep_research_system import run_deep_research_system

# Set page configuration
st.set_page_config(page_title="Deep Research AI", layout="centered")

# Session state setup
if "question" not in st.session_state:
    st.session_state.question = ""
if "show_result" not in st.session_state:
    st.session_state.show_result = False
if "input_key" not in st.session_state:
    st.session_state.input_key = str(uuid.uuid4())  # Unique key for the input field

# Title
st.title("Deep Research AI Agentic System")
st.write("Enter a question below to get the latest insights from web research. Click 'Reset' to start over.")

# Text input (outside form for easier control)
st.session_state.question = st.text_input(
    "Your Question",
    value=st.session_state.question,
    placeholder="e.g., What are the latest advancements in quantum computing?",
    key=st.session_state.input_key
)

# Submit button
if st.button("Get Answer"):
    if st.session_state.question.strip() != "":
        st.session_state.show_result = True
        st.write(f"Research Agent: Searching for '{st.session_state.question}'...")
        try:
            with st.spinner("Gathering research data..."):
                answer = run_deep_research_system(st.session_state.question)
            st.success("Research complete!.Answer Drafter Agent: Drafted the final answer.")
            st.markdown("**Final Answer:**")
            st.write(answer)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
    else:
        st.warning("Please enter a question!")

# Show result
if st.session_state.show_result:
    # Reset button
    if st.button("Reset"):
        # Clear session and reset input widget key to force input clear
        st.session_state.question = ""
        st.session_state.show_result = False
        st.session_state.input_key = str(uuid.uuid4())  # New key forces fresh input widget
        st.rerun()
