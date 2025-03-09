import sys
import logging
import streamlit as st
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # This must be the first Streamlit command
    st.set_page_config(
        page_title="Kidney Dialysis Cost Calculator",
        page_icon="💉",
        layout="wide"
    )

    # Basic title
    st.title("Kidney Dialysis Cost Calculator")

    # Simple test table
    data = {
        'Treatment': ['HD', 'PD', 'APD'],
        'Cost (THB)': [30000, 25000, 35000]
    }
    df = pd.DataFrame(data)

    # CSS for right alignment
    st.markdown("""
    <style>
    .dataframe td:nth-child(2) {
        text-align: right !important;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

    # Format the cost column with thousand separators and ฿ symbol
    df['Cost (THB)'] = df['Cost (THB)'].apply(lambda x: f'฿{x:,.0f}')

    # Display the table
    st.table(df)

    logger.info("Application loaded successfully")

except Exception as e:
    logger.error(f"Application error: {str(e)}")
    st.error(f"Application error: {str(e)}")
    sys.exit(1)