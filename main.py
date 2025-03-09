import streamlit as st
from utils.translations import TRANSLATIONS

# Basic session state
if 'language' not in st.session_state:
    st.session_state.language = 'th'
if 'show_results' not in st.session_state:
    st.session_state.show_results = False
if 'answers' not in st.session_state:
    st.session_state.answers = {}

# Language selector
language = st.selectbox('🌐 Language / ภาษา', ['ไทย', 'English'])
st.session_state.language = 'th' if language == 'ไทย' else 'en'

# Get translations
t = TRANSLATIONS[st.session_state.language]

# Set page config
st.set_page_config(
    page_title=t['title'],
    page_icon="💉",
    layout="wide"
)

# Title
st.title(t['title'])
st.markdown(t['subtitle'])

# Add CSS
st.markdown("""
<style>
.cost-value {
    text-align: right !important;
    font-family: monospace;
    float: right;
    margin-left: 10px;
}
.table-right td:not(:first-child) {
    text-align: right !important;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.show_results:
    with st.form("cost_calculator"):
        # Insurance type
        st.subheader(t['insurance_type'])
        insurance = st.radio(
            t['insurance_type'],
            options=[
                t['insurance_options']['gold_card'],
                t['insurance_options']['civil_servant'],
                t['insurance_options']['social_security'],
                t['insurance_options']['private_insurance'],
                t['insurance_options']['other']
            ],
            key="insurance"
        )

        # Basic Information
        st.subheader(t['basic_info'])
        employment = st.radio(t['employment'], [t['yes'], t['no']], key="employment")

        if employment == t['yes']:
            st.radio(
                t['work_impact'],
                [t['leave_job'], t['work_during_dialysis'], t['no_income_effect']],
                key="work_impact"
            )
            st.number_input(
                t['monthly_income'],
                min_value=0,
                value=0,
                step=1000,
                key="monthly_income"
            )

        # Caregiver needs
        st.subheader(t['caregiver_needs'])
        caregiver_type = st.radio(
            t['caregiver_type'],
            [t['family_caregiver'], t['hired_caregiver'], t['no_caregiver']],
            key="caregiver_type"
        )

        if caregiver_type == t['hired_caregiver']:
            st.info(t['caregiver_costs']['title'] + ":\n" +
                   f"- HD: ฿12,049\n" +
                   f"- CAPD: ฿8,741\n" +
                   f"- APD: ฿11,277")

        # Home Assessment
        st.subheader(t['home_assessment'])
        st.checkbox(t['home_questions']['cleanliness'], key="home_clean")
        st.checkbox(t['home_questions']['sink'], key="home_sink")
        st.checkbox(t['home_questions']['space'], key="home_space")
        st.checkbox(t['home_questions']['crowding'], key="home_private")

        # Treatment Frequency
        st.subheader(t['treatment_frequency'])
        hd_frequency = st.radio(
            t['hd_frequency'],
            [t['freq_2'], t['freq_3']],
            key="hd_frequency"
        )

        # Travel Information
        st.subheader(t['travel_info'])
        st.number_input(
            t['distance'],
            min_value=0,
            value=0,
            step=1,
            key="distance"
        )

        st.number_input(
            t['travel_cost'],
            min_value=0,
            value=0,
            step=10,
            key="travel_cost"
        )

        st.number_input(
            t['food_cost'],
            min_value=0,
            value=0,
            step=10,
            key="food_cost"
        )

        # Calculate button
        submitted = st.form_submit_button(t['calculate'])

        if submitted:
            coverage_factors = {
                t['insurance_options']['gold_card']: 0.05,
                t['insurance_options']['civil_servant']: 0.0,
                t['insurance_options']['social_security']: 0.1,
                t['insurance_options']['private_insurance']: 0.2,
                t['insurance_options']['other']: 0.3
            }

            visits_per_month = 8 if hd_frequency == t['freq_2'] else 12
            coverage_factor = coverage_factors[insurance]

            # Store form data
            for key in st.session_state:
                if key not in ['language', 'show_results']:
                    st.session_state.answers[key] = st.session_state[key]

            # Calculate costs
            detailed_costs = calculate_costs(st.session_state.answers, coverage_factor, visits_per_month)
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

            # Store results
            st.session_state.detailed_costs = detailed_costs
            st.session_state.monthly_totals = monthly_totals
            st.session_state.yearly_costs = yearly_costs
            st.session_state.show_results = True
            st.rerun()

if st.session_state.show_results:
    st.header(t['cost_comparison'])

    # Monthly costs bar chart
    try:
        import pandas as pd
        import plotly.graph_objects as go
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
                         f"฿{st.session_state.monthly_totals[treatment]:,.0f}")
                with st.expander(t['see_details']):
                    for item, cost in st.session_state.detailed_costs[treatment].items():
                        if cost > 0:
                            st.markdown(f"{item}: <div class='cost-value'>฿{cost:,.0f}</div>", unsafe_allow_html=True)

        # Yearly projections
        st.subheader(t['yearly_projections'])
        projections_df = pd.DataFrame({
            t['time_period']: [f"1 {t['year']}", f"5 {t['years']}", f"10 {t['years']}"],
            'HD': [f"฿{st.session_state.yearly_costs['hd'][k]:,.0f}" for k in ['1_year', '5_years', '10_years']],
            'PD': [f"฿{st.session_state.yearly_costs['pd'][k]:,.0f}" for k in ['1_year', '5_years', '10_years']],
            'APD': [f"฿{st.session_state.yearly_costs['apd'][k]:,.0f}" for k in ['1_year', '5_years', '10_years']],
            'CCC': [f"฿{st.session_state.yearly_costs['ccc'][k]:,.0f}" for k in ['1_year', '5_years', '10_years']]
        })

        # Add right-alignment styling
        st.markdown("""
        <style>
        .right-aligned {
            text-align: right !important;
            font-family: monospace;
        }
        .dataframe td:not(:first-child) {
            text-align: right !important;
            font-family: monospace;
        }
        </style>
        """, unsafe_allow_html=True)

        # Display table with right-aligned values
        st.table(projections_df)

        # Action buttons
        cols = st.columns([4, 1, 1])
        with cols[1]:
            if st.button(t['start_over']):
                st.session_state.clear()
                st.rerun()
        with cols[2]:
            if st.button(t['print']):
                st.balloons()

        # Footer notes
        st.markdown("---")
        st.markdown(f"**{t['notes']}:**")
        st.markdown(t['costs_may_vary'])
        st.markdown(t['insurance_note'])
        st.markdown(t['consult_note'])
    except ImportError:
        st.error("Failed to load required libraries. Please refresh the page.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred: {e}")


def calculate_costs(answers, coverage_factor, visits_per_month):
    """Calculate treatment costs based on user inputs"""
    def get_caregiver_cost(treatment_type):
        if answers.get('caregiver_type') == t['hired_caregiver']:
            rates = {
                'hd': 12049,
                'pd': 8741,
                'apd': 11277,
                'ccc': 8741
            }
            return rates.get(treatment_type, 0)
        return 0

    detailed_costs = {
        'hd': {
            t['cost_items']['base_cost']: 30000 * coverage_factor,
            t['cost_items']['medicine']: 5000 * coverage_factor,
            t['cost_items']['travel']: answers.get('travel_cost', 0) * visits_per_month,
            t['cost_items']['food']: answers.get('food_cost', 0) * visits_per_month,
            t['cost_items']['caregiver']: get_caregiver_cost('hd')
        },
        'pd': {
            t['cost_items']['base_cost']: 25000 * coverage_factor,
            t['cost_items']['medicine']: 4000 * coverage_factor,
            t['cost_items']['equipment']: 3000 * coverage_factor,
            t['cost_items']['utilities']: 500,
            t['cost_items']['caregiver']: get_caregiver_cost('pd'),
            t['cost_items']['home_modification']: 5000 if not all([
                answers.get('home_clean', False),
                answers.get('home_sink', False),
                answers.get('home_space', False),
                answers.get('home_private', False)
            ]) else 0
        },
        'apd': {
            t['cost_items']['base_cost']: 35000 * coverage_factor,
            t['cost_items']['medicine']: 4000 * coverage_factor,
            t['cost_items']['equipment']: 5000 * coverage_factor,
            t['cost_items']['utilities']: 1000,
            t['cost_items']['caregiver']: get_caregiver_cost('apd'),
            t['cost_items']['home_modification']: 5000 if not all([
                answers.get('home_clean', False),
                answers.get('home_sink', False),
                answers.get('home_space', False),
                answers.get('home_private', False)
            ]) else 0
        },
        'ccc': {
            t['cost_items']['base_cost']: 15000 * coverage_factor,
            t['cost_items']['medicine']: 3000 * coverage_factor,
            t['cost_items']['caregiver']: get_caregiver_cost('ccc')
        }
    }
    return detailed_costs