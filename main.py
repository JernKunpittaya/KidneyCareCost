import streamlit as st
from components.questions import QuestionFlow
from components.comparison import TreatmentComparison
import base64

# Page configuration
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide"
)

# Load custom CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def initialize_session_state():
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'show_comparison' not in st.session_state:
        st.session_state.show_comparison = False

    # Initialize all possible form field keys
    default_keys = [
        'employment', 'work_impact', 'income', 'caregiver_needs',
        'caregiver_name', 'caregiver_income', 'caregiver_payment',
        'home_suitable', 'clean_corner', 'has_sink', 'home_score',
        'knows_travel_cost', 'travel_cost', 'distance', 'transport_mode'
    ]

    for key in default_keys:
        if key not in st.session_state:
            st.session_state[key] = None

def main():
    load_css()
    initialize_session_state()

    # Header
    st.title("Kidney Dialysis Cost Calculator")
    st.markdown("Calculate and compare treatment costs based on your situation")

    # Progress bar
    if not st.session_state.show_comparison:
        progress = st.session_state.current_step / 10  # Adjust denominator based on total steps
        st.progress(progress)

    # Main content
    if not st.session_state.show_comparison:
        question_flow = QuestionFlow()
        question_flow.show_question()
    else:
        comparison = TreatmentComparison()
        comparison.show_comparison()

    # Footer
    st.markdown("---")
    st.markdown("For medical assistance, please consult with healthcare professionals.")

if __name__ == "__main__":
    main()