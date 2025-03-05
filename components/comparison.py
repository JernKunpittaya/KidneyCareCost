import streamlit as st
from utils.calculator import calculate_costs
from utils.pdf_generator import generate_report

class TreatmentComparison:
    def show_comparison(self):
        st.header("Treatment Comparison Dashboard")
        
        # Calculate costs based on session state answers
        costs = calculate_costs(st.session_state.answers)
        
        # Display cost comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("Hemodialysis (HD)")
            st.markdown(f"Monthly Cost: ฿{costs['hd']:,.2f}")
            st.markdown("### Pros")
            st.markdown("- Professional supervision")
            st.markdown("- Structured schedule")
            st.markdown("### Cons")
            st.markdown("- Regular travel required")
            st.markdown("- Time commitment")

        with col2:
            st.subheader("Peritoneal Dialysis (PD)")
            st.markdown(f"Monthly Cost: ฿{costs['pd']:,.2f}")
            st.markdown("### Pros")
            st.markdown("- Home-based treatment")
            st.markdown("- More flexibility")
            st.markdown("### Cons")
            st.markdown("- Requires storage space")
            st.markdown("- Daily commitment")

        with col3:
            st.subheader("Palliative Care")
            st.markdown(f"Monthly Cost: ฿{costs['palliative']:,.2f}")
            st.markdown("### Pros")
            st.markdown("- Comfort-focused")
            st.markdown("- Less invasive")
            st.markdown("### Cons")
            st.markdown("- Limited treatment")
            st.markdown("- Requires support system")

        # Download report button
        if st.button("Generate Report"):
            pdf = generate_report(st.session_state.answers, costs)
            st.download_button(
                label="Download PDF Report",
                data=pdf,
                file_name="dialysis_cost_report.pdf",
                mime="application/pdf"
            )

        # Reset button
        if st.button("Start Over"):
            st.session_state.clear()
            st.experimental_rerun()
