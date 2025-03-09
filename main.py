import streamlit as st

# Configure the page first, before any other Streamlit commands
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide"
)

try:
    # Basic title and description
    st.title("Kidney Dialysis Cost Calculator")
    st.markdown("Calculate and compare dialysis treatment costs")

    st.success("If you can see this message, the app is working correctly!")

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.stop()