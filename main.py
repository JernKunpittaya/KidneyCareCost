import sys
import streamlit as st

# Add debug information
st.write("Debug: Starting application...")

try:
    # Set page config
    st.set_page_config(
        page_title="Kidney Dialysis Cost Calculator",
        page_icon="💉",
        layout="wide"
    )
    st.write("Debug: Page config set successfully")

    # Simple title and description
    st.title("Kidney Dialysis Cost Calculator")
    st.markdown("Welcome to the cost calculator")
    st.write("Debug: Basic UI elements loaded")

    # Test form with error handling
    try:
        with st.form("test_form"):
            st.write("Basic Information")
            name = st.text_input("Enter your name")
            age = st.number_input("Enter your age", min_value=0, max_value=120)
            submitted = st.form_submit_button("Submit")
            st.write("Debug: Form created successfully")

        if submitted:
            st.success(f"Form submitted for {name}, age {age}")
            st.info("Test message to verify form processing")
            st.write("Debug: Form processed successfully")

    except Exception as form_error:
        st.error(f"Form error: {str(form_error)}")
        st.write(f"Debug: Form error details - {type(form_error).__name__}")

except Exception as e:
    st.error(f"Application error: {str(e)}")
    st.write(f"Debug: Error type - {type(e).__name__}")
    sys.exit(1)

st.write("Debug: Application loaded completely")