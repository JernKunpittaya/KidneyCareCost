import os
import sys
import streamlit as st

# Set page config first, before any other Streamlit commands
try:
    st.set_page_config(
        page_title="Kidney Dialysis Cost Calculator",
        page_icon="💉",
        layout="wide"
    )
except Exception as e:
    st.error(f"Failed to set page config: {str(e)}")
    sys.exit(1)

try:
    # Import other dependencies after page config
    import pandas as pd
    import plotly.graph_objects as go
    from utils.translations import TRANSLATIONS

    # Initialize session state
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

    # Title
    st.title(t['title'])
    st.markdown(t['subtitle'])

    # Custom CSS for better mobile experience and table formatting
    st.markdown("""
        <style>
        /* General table alignment */
        .table-right td:not(:first-child) {
            text-align: right !important;
        }

        /* DataFrame styling */
        .dataframe td:not(:first-child) {
            text-align: right !important;
        }

        /* Cost value alignment */
        .cost-value {
            text-align: right !important;
            font-family: monospace;
            float: right;
            padding-left: 10px;
        }

        /* Streamlit table cell alignment */
        [data-testid="stTable"] table td:not(:first-child) {
            text-align: right !important;
        }

        /* Mobile responsiveness */
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
                ]
            )

            # Basic Information
            st.subheader(t['basic_info'])
            employment = st.radio(t['employment'], [t['yes'], t['no']])

            if employment == t['yes']:
                work_impact = st.radio(
                    t['work_impact'],
                    [t['leave_job'], t['work_during_dialysis'], t['no_income_effect']]
                )
                monthly_income = st.number_input(
                    t['monthly_income'],
                    min_value=0,
                    value=0,
                    step=1000
                )

            # Caregiver needs
            st.subheader(t['caregiver_needs'])
            caregiver_type = st.radio(
                t['caregiver_type'],
                [t['family_caregiver'], t['hired_caregiver'], t['no_caregiver']]
            )

            if caregiver_type == t['hired_caregiver']:
                st.info(f"{t['caregiver_costs']['title']}:\n" +
                       "- HD: ฿12,049\n" +
                       "- CAPD: ฿8,741\n" +
                       "- APD: ฿11,277")

            # Home Assessment
            st.subheader(t['home_assessment'])
            home_clean = st.checkbox(t['home_questions']['cleanliness'])
            home_sink = st.checkbox(t['home_questions']['sink'])
            home_space = st.checkbox(t['home_questions']['space'])
            home_private = st.checkbox(t['home_questions']['crowding'])

            # Treatment Frequency
            st.subheader(t['treatment_frequency'])
            hd_frequency = st.radio(
                t['hd_frequency'],
                [t['freq_2'], t['freq_3']]
            )

            # Travel Information
            st.subheader(t['travel_info'])
            distance = st.number_input(
                t['distance'],
                min_value=0,
                value=0,
                step=1
            )

            travel_cost = st.number_input(
                t['travel_cost'],
                min_value=0,
                value=0,
                step=10
            )

            food_cost = st.number_input(
                t['food_cost'],
                min_value=0,
                value=0,
                step=10
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

                coverage_factor = coverage_factors[insurance]
                visits_per_month = 8 if hd_frequency == t['freq_2'] else 12

                def calculate_caregiver_cost(treatment_type):
                    if caregiver_type == t['hired_caregiver']:
                        rates = {
                            'hd': 12049,
                            'pd': 8741,
                            'apd': 11277,
                            'ccc': 8741
                        }
                        return rates.get(treatment_type, 0)
                    return 0

                # Calculate detailed costs
                detailed_costs = {
                    'hd': {
                        t['cost_items']['base_cost']: 30000 * coverage_factor,
                        t['cost_items']['medicine']: 5000 * coverage_factor,
                        t['cost_items']['travel']: travel_cost * visits_per_month,
                        t['cost_items']['food']: food_cost * visits_per_month,
                        t['cost_items']['caregiver']: calculate_caregiver_cost('hd')
                    },
                    'pd': {
                        t['cost_items']['base_cost']: 25000 * coverage_factor,
                        t['cost_items']['medicine']: 4000 * coverage_factor,
                        t['cost_items']['equipment']: 3000 * coverage_factor,
                        t['cost_items']['utilities']: 500,
                        t['cost_items']['caregiver']: calculate_caregiver_cost('pd'),
                        t['cost_items']['home_modification']: 5000 if not all([home_clean, home_sink, home_space, home_private]) else 0
                    },
                    'apd': {
                        t['cost_items']['base_cost']: 35000 * coverage_factor,
                        t['cost_items']['medicine']: 4000 * coverage_factor,
                        t['cost_items']['equipment']: 5000 * coverage_factor,
                        t['cost_items']['utilities']: 1000,
                        t['cost_items']['caregiver']: calculate_caregiver_cost('apd'),
                        t['cost_items']['home_modification']: 5000 if not all([home_clean, home_sink, home_space, home_private]) else 0
                    },
                    'ccc': {
                        t['cost_items']['base_cost']: 15000 * coverage_factor,
                        t['cost_items']['medicine']: 3000 * coverage_factor,
                        t['cost_items']['caregiver']: calculate_caregiver_cost('ccc')
                    }
                }

                # Calculate monthly totals
                monthly_totals = {
                    treatment: int(sum(costs.values()))
                    for treatment, costs in detailed_costs.items()
                }

                # Calculate yearly projections
                yearly_costs = {}
                for treatment, monthly_cost in monthly_totals.items():
                    yearly_costs[treatment] = {
                        '1_year': int(monthly_cost * 12),
                        '5_years': int(sum([monthly_cost * 12 * (1.03 ** year) for year in range(5)])),
                        '10_years': int(sum([monthly_cost * 12 * (1.03 ** year) for year in range(10)]))
                    }

                # Store results in session state
                st.session_state.detailed_costs = detailed_costs
                st.session_state.monthly_totals = monthly_totals
                st.session_state.yearly_costs = yearly_costs
                st.session_state.show_results = True
    st.experimental_rerun()

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
                            st.markdown(f"{item}: <div class='cost-value'>฿{cost:,.2f}</div>", unsafe_allow_html=True)

        # Yearly projections
        st.subheader(t['yearly_projections'])
        projections_df = pd.DataFrame({
            t['time_period']: [f"1 {t['year']}", f"5 {t['years']}", f"10 {t['years']}"],
            'HD': [f"฿{st.session_state.yearly_costs['hd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'PD': [f"฿{st.session_state.yearly_costs['pd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'APD': [f"฿{st.session_state.yearly_costs['apd'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']],
            'CCC': [f"฿{st.session_state.yearly_costs['ccc'][k]:,.2f}" for k in ['1_year', '5_years', '10_years']]
        })

        # Create a styled table with right-aligned numeric columns
        st.markdown("""
        <style>
        .right-aligned {
            text-align: right !important;
            font-family: monospace;
        }
        </style>
        """, unsafe_allow_html=True)

        # Convert DataFrame to HTML with custom styling
        table_html = projections_df.to_html(classes=['right-aligned'], escape=False, index=False)
        st.markdown(table_html, unsafe_allow_html=True)

        # Action buttons
        cols = st.columns([4, 1, 1])
        with cols[1]:
            if st.button(t['start_over']):
                st.session_state.clear()
                st.experimental_rerun()
        with cols[2]:
            if st.button(t['print']):
                st.balloons()

        # Footer notes
        st.markdown("---")
        st.markdown(f"**{t['notes']}:**")
        st.markdown(t['costs_may_vary'])
        st.markdown(t['insurance_note'])
        st.markdown(t['consult_note'])

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.error("Please try refreshing the page. If the problem persists, contact support.")
    sys.exit(1)