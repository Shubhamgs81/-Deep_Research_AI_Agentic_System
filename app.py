import streamlit as st
from deep_research_system import run_deep_research_system
import traceback
import streamlit.components.v1 as components
 
if __name__ == "__main__":
    # Define API base URL (Update for Hugging Face deployment)
    API_URL = "http://localhost:8000/"

    # Set page configuration
    st.set_page_config(page_title="Deep Research AI", layout="centered")

    # Title and instructions
    st.title("Deep Research AI Agentic System")
    st.write("Enter a question below to get the latest insights from web research. Click 'Reset' to start over.")

    # Initialize session state
    if "show_reset_button" not in st.session_state:
        st.session_state.show_reset_button = False
    if "question" not in st.session_state:
        st.session_state.question = ""
    if "reset_triggered" not in st.session_state:
        st.session_state.reset_triggered = False

    # JavaScript to clear the input field
    clear_input_js = """
    <script>
        const input = document.querySelector('input[aria-label="Your Question"]');
        if (input) {
            input.value = '';
        }
    </script>
    """

    # Use a form to manage the question input and submission
    with st.form(key="question_form"):
        st.session_state.question = st.text_input(
            "Your Question",
            placeholder="e.g., What are the latest advancements in quantum computing?",
            value=st.session_state.question,
            key="question_input"
        )
        submit_button = st.form_submit_button("Get Answer")

    # Process the form submission
    if submit_button:
        if st.session_state.question:
            st.write(f"Research Agent: Searching for '{st.session_state.question}'...")
            try:
                with st.spinner("Gathering research data..."):
                    answer = run_deep_research_system(st.session_state.question)
                st.write("Research Agent: Found 5 relevant sources.")
                st.write("Answer Drafter Agent: Drafted the final answer.")
                st.write("**Final Answer:**")
                st.write(answer)
                st.session_state.show_reset_button = True
            except Exception as e:
                st.error(f"An error occurred: {str(e)}\n{traceback.format_exc()}")
                st.session_state.show_reset_button = True
        else:
            st.warning("Please enter a question!")
        # Reset the trigger flag after submission
        st.session_state.reset_triggered = False

    # Function to clear the input state
    def clear_input():
        st.session_state.show_reset_button = False
        st.session_state.question = ""
        st.session_state.pop("question_input", None)
        st.session_state.pop("question_form", None)
        st.session_state.reset_triggered = True

    # Show Reset button only if show_reset_button is True
    if st.session_state.show_reset_button:
        if st.button("Reset"):
            # Clear the input and reset state
            clear_input()
            # Refresh the webpage
            st.rerun()

    # Execute JavaScript to clear the input field if reset was triggered
    if st.session_state.reset_triggered:
        components.html(clear_input_js, height=0)