import streamlit as st
import pandas as pd

# Set page config first
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide"
)

# Basic test content
st.title("Kidney Dialysis Cost Calculator")
st.markdown("Testing server connectivity")

# Test table with right-aligned numbers

# Create sample data
data = {
    'Period': ['1 Year', '5 Years', '10 Years'],
    'Cost': ['฿100,000', '฿500,000', '฿1,000,000']
}

df = pd.DataFrame(data)

# Custom CSS for right alignment
st.markdown("""
<style>
.dataframe td:nth-child(2) {
    text-align: right !important;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# Display the table
st.table(df)