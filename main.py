import streamlit as st
import pandas as pd

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

        # Medical Information
        st.subheader("Medical Information")
        medical_conditions = st.multiselect(
            "Select any additional medical conditions",
            ["Diabetes", "High Blood Pressure", "Heart Disease", "None"],
            default=["None"]
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

        # Home Assessment
        st.subheader("Home Assessment for PD")
        home_suitable = st.radio(
            "Is your home suitable for peritoneal dialysis?",
            ["Yes", "No", "Not sure"]
        )

        if home_suitable == "Yes":
            has_clean_space = st.checkbox("I have a clean, dust-free space")
            has_storage = st.checkbox("I have storage space for supplies")

        # Travel information
        st.subheader("Travel Information")
        distance = st.number_input(
            "Distance to nearest dialysis center (km)",
            min_value=0,
            value=0,
            step=1
        )

        travel_cost = st.number_input(
            "Cost per visit to dialysis center (THB)",
            min_value=0,
            value=0,
            step=10
        )

        transport_mode = st.selectbox(
            "How will you travel to the center?",
            ["Personal vehicle", "Public transport", "Taxi", "Ambulance"]
        )

        # Submit button
        submitted = st.form_submit_button("Calculate Costs")

        if submitted:
            # Calculate basic costs
            visits_per_month = 13  # Assuming 13 visits per month

            # Base costs
            hd_cost = 30000  # Base Hemodialysis cost
            pd_cost = 25000  # Base Peritoneal Dialysis cost
            palliative_cost = 15000  # Base Palliative care cost

            # Add travel costs for HD
            if transport_mode == "Ambulance":
                travel_cost = max(travel_cost, 1000)  # Minimum ambulance cost
            hd_cost += (travel_cost * visits_per_month)

            # Add care costs
            if care_needs == "Need assistance with travel only":
                care_cost = 5000
                hd_cost += care_cost
                pd_cost += care_cost * 0.5  # Less travel needed for PD
                palliative_cost += care_cost
            elif care_needs == "Need daily assistance":
                care_cost = 15000
                hd_cost += care_cost
                pd_cost += care_cost
                palliative_cost += care_cost

            # Adjust PD cost based on home suitability
            if home_suitable == "No":
                pd_cost += 5000  # Additional cost for home modifications

            # Store monthly costs
            monthly_costs = {
                'hd': hd_cost,
                'pd': pd_cost,
                'palliative': palliative_cost
            }

            # Calculate yearly projections (including 3% annual increase)
            yearly_costs = {}
            for treatment, monthly_cost in monthly_costs.items():
                yearly_costs[treatment] = {
                    '1_year': monthly_cost * 12,
                    '5_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(5)]),
                    '10_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(10)])
                }

            st.session_state.costs = monthly_costs
            st.session_state.yearly_costs = yearly_costs
            st.session_state.show_results = True
            st.rerun()

# Show results if calculation is done
if st.session_state.show_results:
    st.header("Treatment Cost Comparison")

    # Monthly costs
    st.subheader("Monthly Costs")
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

    # Yearly projections
    st.subheader("Cost Projections")
    projections_df = pd.DataFrame({
        'Time Period': ['1 Year', '5 Years', '10 Years'],
        'Hemodialysis (HD)': [
            f"฿{st.session_state.yearly_costs['hd']['1_year']:,.2f}",
            f"฿{st.session_state.yearly_costs['hd']['5_years']:,.2f}",
            f"฿{st.session_state.yearly_costs['hd']['10_years']:,.2f}"
        ],
        'Peritoneal Dialysis (PD)': [
            f"฿{st.session_state.yearly_costs['pd']['1_year']:,.2f}",
            f"฿{st.session_state.yearly_costs['pd']['5_years']:,.2f}",
            f"฿{st.session_state.yearly_costs['pd']['10_years']:,.2f}"
        ],
        'Palliative Care': [
            f"฿{st.session_state.yearly_costs['palliative']['1_year']:,.2f}",
            f"฿{st.session_state.yearly_costs['palliative']['5_years']:,.2f}",
            f"฿{st.session_state.yearly_costs['palliative']['10_years']:,.2f}"
        ]
    })

    st.table(projections_df)

    if st.button("Start Over"):
        st.session_state.show_results = False
        st.rerun()

    # Footer with notes
    st.markdown("---")
    st.markdown("""
    **Notes:**
    - Costs are estimates and may vary based on individual circumstances
    - Yearly projections include a 3% annual increase for inflation
    - Consult healthcare professionals for medical advice
    """)