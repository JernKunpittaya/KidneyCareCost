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

    # Title with enhanced styling
    st.markdown(f"<div class='main-header'><h1>{t['title']}</h1><p>{t['subtitle']}</p></div>", unsafe_allow_html=True)

    # Custom CSS for better experience and visual design
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Roboto+Mono&display=swap');

        /* Main theme colors */
        :root {
            --primary-color: #1e88e5;
            --secondary-color: #26a69a;
            --background-color: #ffffff;
            --text-color: #2c3e50;
            --light-gray: #f8f9fa;
            --card-shadow: none; /* Modified: Removed box shadow */
            --border-radius: 8px;
        }

        /* General styling */
        .main {
            font-family: 'Roboto', sans-serif;
        }

        /* Header styling */
        .main-header {
            background-color: var(--light-gray); /* Use variable for consistency */
            padding: 1.5rem;
            border-radius: var(--border-radius); /* Use variable for consistency */
            margin-bottom: 2rem;
            border-left: 5px solid var(--primary-color); /* Use variable for consistency */
        }

        /* Section styling */
        .section-container {
            background-color: var(--background-color); /* Use variable for consistency */
            padding: 1.5rem;
            border-radius: var(--border-radius); /* Use variable for consistency */
            /*box-shadow: var(--card-shadow); Removed box-shadow */
            margin-bottom: 1.5rem;
        }

        /* General table alignment */
        .table-right td:not(:first-child) {
            text-align: right !important;
        }

        /* DataFrame styling */
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: var(--border-radius); /* Use variable for consistency */
            overflow: hidden;
            /*box-shadow: var(--card-shadow); Removed box-shadow */
        }

        .dataframe th {
            background-color: var(--primary-color); /* Use variable for consistency */
            color: white;
            padding: 12px;
            text-align: left !important;
        }

        .dataframe td {
            padding: 10px;
            border-bottom: 1px solid #e0e0e0;
        }

        .dataframe td:not(:first-child) {
            text-align: right !important;
            font-family: 'Roboto Mono', monospace;
        }

        .dataframe tr:nth-child(even) {
            background-color: var(--light-gray); /* Use variable for consistency */
        }

        /* Cost breakdown styling */
        .cost-breakdown {
            border-radius: var(--border-radius);
            padding: 10px 0;
            margin-top: 10px;
            border: 1px solid #e0e0e0;
            width: 100%;
            box-sizing: border-box;
        }
        
        .cost-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
            width: 100%;
            box-sizing: border-box;
        }
        
        .cost-item:last-child {
            border-bottom: none;
        }
        
        .cost-label {
            font-weight: 500;
            color: var(--text-color);
            flex: 1;
            padding-right: 10px;
        }
        
        .cost-value {
            text-align: right !important;
            font-family: 'Roboto Mono', monospace;
            padding: 5px 10px;
            background-color: rgba(30, 136, 229, 0.1);
            border-radius: 4px;
            color: var(--primary-color); /* Use variable for consistency */
            font-weight: 600;
            min-width: 80px;
            text-align: center;
            display: inline-block;
            white-space: nowrap;
        }

        /* Streamlit table cell alignment */
        [data-testid="stTable"] table td:not(:first-child) {
            text-align: right !important;
        }

        /* Form styling */
        .stForm > div {
            background-color: var(--background-color); /* Use variable for consistency */
            padding: 1.5rem;
            border-radius: var(--border-radius); /* Use variable for consistency */
            /*box-shadow: var(--card-shadow); Removed box-shadow */
        }

        /* Treatment cards */
        .treatment-card {
            background-color: var(--background-color); /* Use variable for consistency */
            padding: 20px;
            border-radius: var(--border-radius); /* Use variable for consistency */
            /*box-shadow: var(--card-shadow); Removed box-shadow */
            margin: 15px 0;
            border-top: 4px solid var(--primary-color); /* Use variable for consistency */
            transition: all 0.3s ease;
            width: 100%;
            box-sizing: border-box;
        }
        
        /* Column spacing for treatment cards */
        [data-testid="column"] {
            box-sizing: border-box;
        }

        /* Responsive design - desktop, tablet and mobile */
        @media (min-width: 992px) {
            .cost-item {
                padding: 12px 20px;
            }
            .cost-value {
                min-width: 100px;
            }
            .cost-breakdown {
                max-width: 90%;
                margin: 10px auto;
            }
        }
        
        /* Medium screens (tablets and small desktops) */
        @media (min-width: 641px) and (max-width: 991px) {
            .section-container {
                padding: 1rem;
            }
            .cost-item {
                padding: 10px 15px;
            }
            .cost-value {
                min-width: 85px;
                font-size: 0.9rem;
            }
            [data-testid="column"] > div {
                padding: 0.5rem !important;
            }
            /* Adjust expander content */
            .streamlit-expanderContent {
                padding: 10px !important;
            }
            /* Ensure cost breakdown fits within the cards */
            .cost-breakdown {
                width: 100%;
                margin: 5px 0;
            }
            /* Better alignment for cost details */
            .cost-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                width: 100%;
            }
            .cost-label {
                max-width: 65%;
            }
        }
        
        @media (max-width: 640px) {
            .main > div {
                padding: 1rem 0.5rem;
            }
            .stMarkdown p {
                font-size: 0.9rem;
            }
            .cost-item {
                padding: 10px 12px;
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
                st.rerun()

    if st.session_state.show_results:
        st.header(t['cost_comparison'])

        # Monthly costs bar chart with enhanced colors and styling
        colors = ['#1e88e5', '#26a69a', '#7e57c2', '#ef5350']

        fig = go.Figure(data=[
            go.Bar(
                x=[t['treatment_types'][k] for k in ['hd', 'pd', 'apd', 'ccc']],
                y=[st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']],
                text=[f"฿{int(cost):,}" for cost in [st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']]],
                textposition='auto',
                marker_color=colors,
                marker_line_width=0,
                hoverinfo='y+text',
                hoverlabel=dict(
                    bgcolor='white',
                    font_size=16,
                    font_family="Roboto"
                )
            )
        ])

        fig.update_layout(
            title={
                'text': t['monthly_overview'],
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=22, color='#2c3e50')
            },
            yaxis_title={
                'text': 'Monthly Cost (THB)',
                'font': dict(size=16, color='#2c3e50')
            },
            height=450,
            margin=dict(t=80, b=20, l=20, r=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Roboto"),
            xaxis=dict(
                tickfont=dict(size=14, color='#2c3e50'),
                gridcolor='#f8f9fa'
            ),
            yaxis=dict(
                tickfont=dict(size=14, color='#2c3e50'),
                gridcolor='#f8f9fa',
                showgrid=True
            ),
            bargap=0.3,
            hoverlabel=dict(
                bgcolor="white",
                font_size=16,
                font_family="Roboto"
            )
        )

        # Chart container styling
        st.markdown("""
        <div style="background-color: white; padding: 20px; border-radius: 8px;">
        """, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Detailed breakdown for each treatment with enhanced styling
        st.markdown(f"<div class='section-container'><h2>{t['monthly_overview']}</h2>", unsafe_allow_html=True)
        cols = st.columns(4)

        treatment_colors = {
            'hd': '#1e88e5',  # Blue
            'pd': '#26a69a',  # Teal
            'apd': '#7e57c2', # Purple
            'ccc': '#ef5350'  # Red
        }

        for i, (treatment, label) in enumerate([
            ('hd', 'HD'), ('pd', 'PD'), ('apd', 'APD'), ('ccc', 'CCC')
        ]):
            with cols[i]:
                # Custom styled card for each treatment
                st.markdown(f"""
                <div style='background-color: white; padding: 15px; border-radius: 8px; 
                            border-top: 4px solid {treatment_colors[treatment]};'>
                    <h3 style='color: {treatment_colors[treatment]}; margin-bottom: 10px;'>{t['treatment_types'][treatment]}</h3>
                    <div style='font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-bottom: 5px;'>
                        ฿{st.session_state.monthly_totals[treatment]:,}
                    </div>
                    <div style='font-size: 0.8rem; color: #7f8c8d;'>{t['per_month']}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(t['see_details']):
                    st.markdown("<div class='cost-breakdown'>", unsafe_allow_html=True)
                    for item, cost in st.session_state.detailed_costs[treatment].items():
                        if cost > 0:
                            st.markdown(f"<div class='cost-item'><span class='cost-label'>{item}:</span><span class='cost-value'>฿{int(cost):,}</span></div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # Close the section container

        # Yearly projections with enhanced styling
        st.markdown(f"<div class='section-container'><h2>{t['yearly_projections']}</h2>", unsafe_allow_html=True)

        # Create dataframe for projections
        projections_df = pd.DataFrame({
            t['time_period']: [f"1 {t['year']}", f"5 {t['years']}", f"10 {t['years']}"],
            'HD': [f"฿{st.session_state.yearly_costs['hd'][k]:,}" for k in ['1_year', '5_years', '10_years']],
            'PD': [f"฿{st.session_state.yearly_costs['pd'][k]:,}" for k in ['1_year', '5_years', '10_years']],
            'APD': [f"฿{st.session_state.yearly_costs['apd'][k]:,}" for k in ['1_year', '5_years', '10_years']],
            'CCC': [f"฿{st.session_state.yearly_costs['ccc'][k]:,}" for k in ['1_year', '5_years', '10_years']]
        })

        # Create custom HTML for better styling
        html_table = f"""
        <table class="dataframe">
            <thead>
                <tr>
                    <th>{t['time_period']}</th>
                    <th style="background-color: #1e88e5;">HD</th>
                    <th style="background-color: #26a69a;">PD</th>
                    <th style="background-color: #7e57c2;">APD</th>
                    <th style="background-color: #ef5350;">CCC</th>
                </tr>
            </thead>
            <tbody>
        """

        for i, row in projections_df.iterrows():
            html_table += "<tr>"
            html_table += f"<td>{row[t['time_period']]}</td>"
            html_table += f"<td>{row['HD']}</td>"
            html_table += f"<td>{row['PD']}</td>"
            html_table += f"<td>{row['APD']}</td>"
            html_table += f"<td>{row['CCC']}</td>"
            html_table += "</tr>"

        html_table += """
            </tbody>
        </table>
        </div>
        """

        st.markdown(html_table, unsafe_allow_html=True)

        # Action buttons
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        cols = st.columns([4, 1, 1])
        with cols[1]:
            if st.button(t['start_over'], use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with cols[2]:
            if st.button(t['print'], use_container_width=True):
                st.balloons()
        st.markdown("</div>", unsafe_allow_html=True)

        # Footer notes
        st.markdown("<div class='section-container footer-notes'>", unsafe_allow_html=True)
        st.markdown(f"**{t['notes']}:**")
        st.markdown(t['costs_may_vary'])
        st.markdown(t['insurance_note'])
        st.markdown(t['consult_note'])
        st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.error("Please try refreshing the page. If the problem persists, contact support.")
    sys.exit(1)