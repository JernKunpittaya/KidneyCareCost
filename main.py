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

        # Caregiver details
        if care_needs != "No assistance needed":
            st.subheader("Caregiver Details")
            caregiver_income = st.number_input(
                "Caregiver's monthly income (THB)",
                min_value=0,
                value=0,
                step=1000
            )

        # Home Assessment
        st.subheader("Home Assessment")
        home_suitable = st.radio(
            "Is your home suitable for peritoneal dialysis?",
            ["Yes", "No", "Not sure"]
        )

        # Utilities cost for PD
        utilities_cost = st.number_input(
            "Monthly utilities cost (water, electricity) (THB)",
            min_value=0,
            value=0,
            step=100
        )

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

        food_cost = st.number_input(
            "Food and refreshments cost per visit (THB)",
            min_value=0,
            value=0,
            step=10
        )

        # Submit button
        submitted = st.form_submit_button("Calculate Costs")

        if submitted:
            # Base costs
            base_costs = {
                'apd': 30000,    # Base APD cost
                'capd': 25000,   # Base CAPD cost
                'hd': 30000      # Base HD cost
            }

            # Calculate detailed costs
            detailed_costs = {
                'apd': {
                    'accounting': {
                        'base_cost': base_costs['apd'],
                        'utilities': utilities_cost,
                        'caregiver': 0 if care_needs == "No assistance needed" else 15000
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == "No assistance needed" else (caregiver_income * 0.1),
                        'patient_lost_income': monthly_income * 0.1 if employment == "Yes" else 0
                    }
                },
                'capd': {
                    'accounting': {
                        'base_cost': base_costs['capd'],
                        'caregiver': 0 if care_needs == "No assistance needed" else 15000
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == "No assistance needed" else (caregiver_income * 0.15),
                        'patient_lost_income': monthly_income * 0.15 if employment == "Yes" else 0
                    }
                },
                'hd': {
                    'accounting': {
                        'base_cost': base_costs['hd'],
                        'travel': travel_cost * 13,  # 13 visits per month
                        'caregiver': 0 if care_needs == "No assistance needed" else 15000,
                        'food': food_cost * 13  # 13 visits per month
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == "No assistance needed" else (caregiver_income * 0.3),
                        'patient_lost_income': monthly_income * 0.3 if employment == "Yes" else 0
                    }
                }
            }

            # Calculate totals
            monthly_totals = {}
            for treatment in detailed_costs:
                accounting = sum(detailed_costs[treatment]['accounting'].values())
                opportunity = sum(detailed_costs[treatment]['opportunity'].values())
                monthly_totals[treatment] = accounting + opportunity

            # Calculate yearly projections (including 3% annual increase)
            yearly_costs = {}
            for treatment, monthly_cost in monthly_totals.items():
                yearly_costs[treatment] = {
                    '1_year': monthly_cost * 12,
                    '5_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(5)]),
                    '10_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(10)])
                }

            st.session_state.detailed_costs = detailed_costs
            st.session_state.monthly_totals = monthly_totals
            st.session_state.yearly_costs = yearly_costs
            st.session_state.show_results = True
            st.rerun()

# Show results if calculation is done
if st.session_state.show_results:
    st.header("Treatment Cost Comparison")

    # Monthly costs summary
    st.subheader("Monthly Costs Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Automated PD (APD)", f"฿{st.session_state.monthly_totals['apd']:,.2f}")
        with st.expander("See detailed breakdown"):
            st.markdown("### Accounting Costs")
            for key, value in st.session_state.detailed_costs['apd']['accounting'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")
            st.markdown("### Opportunity Costs")
            for key, value in st.session_state.detailed_costs['apd']['opportunity'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")

    with col2:
        st.metric("Continuous APD (CAPD)", f"฿{st.session_state.monthly_totals['capd']:,.2f}")
        with st.expander("See detailed breakdown"):
            st.markdown("### Accounting Costs")
            for key, value in st.session_state.detailed_costs['capd']['accounting'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")
            st.markdown("### Opportunity Costs")
            for key, value in st.session_state.detailed_costs['capd']['opportunity'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")

    with col3:
        st.metric("Hemodialysis (HD)", f"฿{st.session_state.monthly_totals['hd']:,.2f}")
        with st.expander("See detailed breakdown"):
            st.markdown("### Accounting Costs")
            for key, value in st.session_state.detailed_costs['hd']['accounting'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")
            st.markdown("### Opportunity Costs")
            for key, value in st.session_state.detailed_costs['hd']['opportunity'].items():
                st.markdown(f"- {key.replace('_', ' ').title()}: ฿{value:,.2f}")

    # Long-term projections
    st.subheader("Long-term Cost Projections")
    with st.expander("See yearly projections"):
        projections_df = pd.DataFrame({
            'Time Period': ['1 Year', '5 Years', '10 Years'],
            'APD': [
                f"฿{st.session_state.yearly_costs['apd']['1_year']:,.2f}",
                f"฿{st.session_state.yearly_costs['apd']['5_years']:,.2f}",
                f"฿{st.session_state.yearly_costs['apd']['10_years']:,.2f}"
            ],
            'CAPD': [
                f"฿{st.session_state.yearly_costs['capd']['1_year']:,.2f}",
                f"฿{st.session_state.yearly_costs['capd']['5_years']:,.2f}",
                f"฿{st.session_state.yearly_costs['capd']['10_years']:,.2f}"
            ],
            'HD': [
                f"฿{st.session_state.yearly_costs['hd']['1_year']:,.2f}",
                f"฿{st.session_state.yearly_costs['hd']['5_years']:,.2f}",
                f"฿{st.session_state.yearly_costs['hd']['10_years']:,.2f}"
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