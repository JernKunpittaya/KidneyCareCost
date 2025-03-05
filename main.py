import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide"
)

# Initialize session state
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Title
st.title("Kidney Dialysis Cost Calculator")
st.markdown("Calculate and compare treatment costs based on your situation")

# Only show form if not showing results
if not st.session_state.show_results:
    with st.form("cost_calculator"):
        # Basic information
        st.subheader("Basic Information")
        employment = st.radio("Are you currently working?", ["Yes", "No"])

        monthly_income = st.number_input(
            "Monthly income (THB)",
            min_value=0,
            value=0,
            step=1000
        )

        # Care needs
        st.subheader("Care Requirements")
        care_needs = st.radio(
            "Do you require assistance?",
            [
                "No assistance needed",
                "Need assistance with travel only",
                "Need daily assistance"
            ]
        )

        # Travel information
        st.subheader("Travel Information")
        travel_cost = st.number_input(
            "Cost per visit to dialysis center (THB)",
            min_value=0,
            value=0,
            step=10
        )

        # Submit button
        submitted = st.form_submit_button("Calculate Costs")

        if submitted:
            # Calculate basic costs
            visits_per_month = 13  # Assuming 13 visits per month

            # Calculate costs
            hd_cost = 30000 + (travel_cost * visits_per_month)  # Base cost + travel
            pd_cost = 25000  # Base cost for PD
            palliative_cost = 15000  # Base cost for palliative

            # Add care costs if needed
            if care_needs != "No assistance needed":
                care_cost = 5000 if care_needs == "Need assistance with travel only" else 15000
                hd_cost += care_cost
                pd_cost += care_cost
                palliative_cost += care_cost

            # Store results
            st.session_state.costs = {
                'hd': hd_cost,
                'pd': pd_cost,
                'palliative': palliative_cost
            }
            st.session_state.show_results = True
            st.rerun()

# Show results if calculation is done
if st.session_state.show_results:
    st.header("Treatment Cost Comparison")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Hemodialysis (HD)")
        st.markdown(f"Monthly Cost: ฿{st.session_state.costs['hd']:,.2f}")
        st.markdown("- Regular hospital visits")
        st.markdown("- Professional supervision")

    with col2:
        st.subheader("Peritoneal Dialysis (PD)")
        st.markdown(f"Monthly Cost: ฿{st.session_state.costs['pd']:,.2f}")
        st.markdown("- Home-based treatment")
        st.markdown("- More flexibility")

    with col3:
        st.subheader("Palliative Care")
        st.markdown(f"Monthly Cost: ฿{st.session_state.costs['palliative']:,.2f}")
        st.markdown("- Comfort-focused care")
        st.markdown("- Less invasive")

    if st.button("Start Over"):
        st.session_state.show_results = False
        st.rerun()