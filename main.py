import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.translations import TRANSLATIONS

# Page configuration
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better mobile experience
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        margin: 1rem 0;
    }
    @media (max-width: 640px) {
        .main > div {
            padding: 1rem 0.5rem;
        }
        .stMarkdown p {
            font-size: 0.9rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'th'
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Language selector
language = st.selectbox('🌐 Language / ภาษา', ['ไทย', 'English'])
st.session_state.language = 'th' if language == 'ไทย' else 'en'

# Get translations
t = TRANSLATIONS[st.session_state.language]

# Title
st.title(t['title'])
st.markdown(t['subtitle'])

if not st.session_state.show_results:
    with st.form("cost_calculator"):
        # Insurance type
        st.subheader(t['insurance_type'])
        st.info(t.get('insurance_note', "Your insurance type significantly affects your out-of-pocket expenses for dialysis treatments."))
        insurance = st.radio(
            t['insurance_type'],
            options=[
                t['insurance_options']['gold_card'],
                t['insurance_options']['civil_servant'],
                t['insurance_options']['social_security'],
                t['insurance_options']['private_insurance'],
                t['insurance_options']['other'],
                t.get('insurance_options', {}).get('no_insurance', "No insurance")
            ]
        )

        # Basic Information
        st.subheader(t['basic_info'])
        st.info(t.get('basic_info_note', "This information helps us understand how dialysis may impact your work and income."))
        employment = st.radio(t['employment'], [t['yes'], t['no']])

        if employment == t['yes']:
            work_impact = st.radio(
                t['work_impact'],
                [t['leave_job'], t['work_during_dialysis'], t['no_income_effect']]
            )
            st.info(t.get('income_note', "Your income helps us calculate the economic impact of different treatment options."))
            
            # Income selection
            income_type = st.radio(
                t.get('income_type', "How do you receive your income?"),
                [t.get('monthly_salary', "Monthly salary"), t.get('lump_sum', "Lump sum payments"), t.get('no_income', "No income")]
            )
            
            if income_type == t.get('monthly_salary', "Monthly salary"):
                monthly_income = st.number_input(
                    t['monthly_income'],
                    min_value=0,
                    value=0,
                    step=1000
                )
            elif income_type == t.get('lump_sum', "Lump sum payments"):
                annual_income = st.number_input(
                    t.get('annual_income', "Please enter your annual income (THB):"),
                    min_value=0,
                    value=0,
                    step=10000
                )
                # Convert to monthly for calculations
                monthly_income = annual_income / 12
                st.info(f"{t.get('estimated_monthly', 'Your estimated monthly income:')} ฿{monthly_income:,.2f}")
            else:
                monthly_income = 0

        # Caregiver needs
        st.subheader(t['caregiver_needs'])
        st.info(t.get('caregiver_note', "Different treatments require different levels of assistance. This helps us estimate potential caregiver costs."))
        caregiver_type = st.radio(
            t['caregiver_type'],
            [t['family_caregiver'], t['hired_caregiver'], t['no_caregiver']]
        )

        if caregiver_type == t['hired_caregiver']:
            caregiver_cost = st.number_input(
                t['caregiver_cost'],
                min_value=0,
                value=0,
                step=1000
            )

        # Home Assessment
        st.subheader(t['home_assessment'])
        st.info(t.get('home_note', "Peritoneal dialysis (PD) requires a clean environment and basic amenities at home. This helps determine if your home is suitable for PD treatment."))
        home_clean = st.checkbox(t['home_questions']['cleanliness'], help=t.get('clean_help', "Clean environment reduces infection risk"))
        home_sink = st.checkbox(t['home_questions']['sink'], help=t.get('sink_help', "Proper hand hygiene is essential"))
        home_space = st.checkbox(t['home_questions']['space'], help=t.get('space_help', "Space for supplies and equipment"))
        home_private = st.checkbox(t['home_questions']['crowding'], help=t.get('crowding_help', "Privacy is important for treatment"))

        # Treatment Frequency
        st.subheader(t['treatment_frequency'])
        hd_frequency = st.radio(
            t['hd_frequency'],
            [t['freq_2'], t['freq_3']]
        )

        # Travel Information
        st.subheader(t['travel_info'])
        st.info(t.get('travel_note', "Hemodialysis typically requires 2-3 trips to a dialysis center per week. Travel costs can be significant over time."))
        distance = st.number_input(
            t['distance'],
            min_value=0,
            value=0,
            step=1,
            help=t.get('distance_help', "Distance to nearest dialysis center in kilometers")
        )

        travel_cost = st.number_input(
            t['travel_cost'],
            min_value=0,
            value=0,
            step=10,
            help=t.get('travel_cost_help', "Cost per one-way trip")
        )

        food_cost = st.number_input(
            t['food_cost'],
            min_value=0,
            value=0,
            step=10,
            help=t.get('food_cost_help', "Food expenses during treatment days")
        )

        # Calculate button
        submitted = st.form_submit_button(t['calculate'])

        if submitted:
            # Base costs by insurance type (example values, adjust based on actual coverage)
            coverage_factors = {
                t['insurance_options']['gold_card']: 0.05,      # 5% of total cost
                t['insurance_options']['civil_servant']: 0.0,   # 0% of total cost
                t['insurance_options']['social_security']: 0.1, # 10% of total cost
                t['insurance_options']['private_insurance']: 0.2, # 20% of total cost
                t['insurance_options']['other']: 0.3,           # 30% of total cost
                t.get('insurance_options', {}).get('no_insurance', "No insurance"): 1.0  # 100% of total cost (full price)
            }

            # Get coverage factor with fallback to full cost (1.0) if insurance type not found
            coverage_factor = coverage_factors.get(insurance, 1.0)
            visits_per_month = 8 if hd_frequency == t['freq_2'] else 12

            # Calculate detailed costs
            detailed_costs = {
                'hd': {
                    t['cost_items']['base_cost']: 30000 * coverage_factor,
                    t['cost_items']['medicine']: 5000 * coverage_factor,
                    t['cost_items']['travel']: travel_cost * visits_per_month,
                    t['cost_items']['food']: food_cost * visits_per_month,
                    t['cost_items']['caregiver']: caregiver_cost if caregiver_type == t['hired_caregiver'] else 0
                },
                'pd': {
                    t['cost_items']['base_cost']: 25000 * coverage_factor,
                    t['cost_items']['medicine']: 4000 * coverage_factor,
                    t['cost_items']['equipment']: 3000 * coverage_factor,
                    t['cost_items']['utilities']: 500,
                    t['cost_items']['caregiver']: caregiver_cost if caregiver_type == t['hired_caregiver'] else 0,
                    t['cost_items']['home_modification']: 5000 if not all([home_clean, home_sink, home_space, home_private]) else 0
                },
                'apd': {
                    t['cost_items']['base_cost']: 35000 * coverage_factor,
                    t['cost_items']['medicine']: 4000 * coverage_factor,
                    t['cost_items']['equipment']: 5000 * coverage_factor,
                    t['cost_items']['utilities']: 1000,
                    t['cost_items']['caregiver']: caregiver_cost if caregiver_type == t['hired_caregiver'] else 0,
                    t['cost_items']['home_modification']: 5000 if not all([home_clean, home_sink, home_space, home_private]) else 0
                },
                'ccc': {
                    t['cost_items']['base_cost']: 15000 * coverage_factor,
                    t['cost_items']['medicine']: 3000 * coverage_factor,
                    t['cost_items']['caregiver']: caregiver_cost if caregiver_type == t['hired_caregiver'] else 0
                }
            }

            # Calculate monthly totals
            monthly_totals = {
                treatment: sum(costs.values())
                for treatment, costs in detailed_costs.items()
            }

            # Calculate yearly projections
            yearly_costs = {}
            for treatment, monthly_cost in monthly_totals.items():
                yearly_costs[treatment] = {
                    '1_year': monthly_cost * 12,
                    '5_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(5)]),
                    '10_years': sum([monthly_cost * 12 * (1.03 ** year) for year in range(10)])
                }

            # Store results in session state
            st.session_state.detailed_costs = detailed_costs
            st.session_state.monthly_totals = monthly_totals
            st.session_state.yearly_costs = yearly_costs
            st.session_state.show_results = True
            st.rerun()

if st.session_state.show_results:
    st.header(t['cost_comparison'])

    # Monthly costs bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=[t['treatment_types'][k] for k in ['hd', 'pd', 'apd', 'ccc']],
            y=[st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']],
            text=[f"฿{cost:,.0f}" for cost in [st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']]],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title=t['monthly_overview'],
        yaxis_title='Monthly Cost (THB)',
        height=400,
        margin=dict(t=50, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed breakdown for each treatment
    st.subheader(t['monthly_overview'])
    cols = st.columns(4)

    for i, (treatment, label) in enumerate([
        ('hd', 'HD'), ('pd', 'PD'), ('apd', 'APD'), ('ccc', 'CCC')
    ]):
        with cols[i]:
            st.metric(t['treatment_types'][treatment], 
                     f"฿{st.session_state.monthly_totals[treatment]:,.2f}")
            with st.expander(t['see_details']):
                for item, cost in st.session_state.detailed_costs[treatment].items():
                    if cost > 0:
                        st.markdown(f"- {item}: ฿{cost:,.2f}")

    # Yearly projections
    st.subheader(t['yearly_projections'])
    with st.expander(t['yearly_projections']):
        projections_df = pd.DataFrame({
            'Time Period': ['1 Year', '5 Years', '10 Years'],
            'HD': [f"฿{st.session_state.yearly_costs['hd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'PD': [f"฿{st.session_state.yearly_costs['pd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'APD': [f"฿{st.session_state.yearly_costs['apd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'CCC': [f"฿{st.session_state.yearly_costs['ccc'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']]
        })
        st.table(projections_df)

    if st.button(t['start_over']):
        st.session_state.show_results = False
        st.rerun()

    # Footer notes
    st.markdown("---")
    st.markdown(f"**{t['notes']}:**")
    st.markdown(t['costs_may_vary'])
    st.markdown(t['insurance_note'])
    st.markdown(t['consult_note'])