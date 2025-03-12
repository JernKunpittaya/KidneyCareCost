import os
import sys
import streamlit as st
import streamlit.components.v1 as components

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
            margin-bottom: 2rem; /* Increased margin for better section separation */
        }
        
        /* Section headers styling */
        .section-container h2 {
            margin-top: 0;
            margin-bottom: 1.2rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid #e0e0e0;
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
            border: none;
            width: 100%;
            box-sizing: border-box;
        }
        
        /* Add spacing to bullet points for better readability */
        .cost-breakdown ul {
            margin: 0;
            padding-left: 1.2rem;
        }
        
        .cost-breakdown li {
            margin-bottom: 0.6rem;
        }

        .cost-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 15px; /* Reduced vertical padding for tighter grouping */
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
        
        /* Form section styling */
        .stForm .stSubheader {
            margin-top: 1.8rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #f0f0f0;
            color: var(--primary-color);
        }
        
        /* First subheader needs less top margin */
        .stForm .stSubheader:first-of-type {
            margin-top: 0.5rem;
        }
        
        /* Group related form elements */
        .stForm .stRadio, .stForm .stNumberInput, .stForm .stCheckbox {
            margin-bottom: 1.2rem;
            padding-left: 0.8rem;
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
                padding: 10px 20px;
            }
            .cost-value {
                min-width: 100px;
            }
            .cost-breakdown {
                max-width: 90%;
                margin: 10px auto;
            }
            /* Consistent column spacing for treatment cards */
            [data-testid="column"] {
                padding: 0.5rem !important;
            }
        }

        /* Medium screens (tablets and small desktops) */
        @media (min-width: 641px) and (max-width: 991px) {
            .section-container {
                padding: 1.2rem;
                margin-bottom: 1.5rem; /* Reduced margin for tablet */
            }
            .cost-item {
                padding: 8px 15px;
            }
            .cost-value {
                min-width: 85px;
                font-size: 0.9rem;
            }
            [data-testid="column"] > div {
                padding: 0.4rem !important;
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
            /* Reduce form element spacing */
            .stForm .stRadio, .stForm .stNumberInput, .stForm .stCheckbox {
                margin-bottom: 0.8rem;
            }
        }

        @media (max-width: 640px) {
            .main > div {
                padding: 0.8rem 0.5rem;
            }
            .stMarkdown p {
                font-size: 0.9rem;
            }
            .cost-item {
                padding: 8px 12px;
            }
            .section-container {
                padding: 1rem;
                margin-bottom: 1.2rem; /* More compact for mobile */
            }
            /* Tighter spacing for form elements on mobile */
            .stForm .stRadio, .stForm .stNumberInput, .stForm .stCheckbox {
                margin-bottom: 0.6rem;
            }
            .stForm .stSubheader {
                margin-top: 1.5rem;
                margin-bottom: 0.8rem;
            }
        }
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: var(--light-gray);
            border-radius: var(--border-radius) var(--border-radius) 0 0;
            padding: 8px 15px !important;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .streamlit-expanderContent {
            border: none;
            border-radius: 0 0 var(--border-radius) var(--border-radius);
            padding: 12px !important;
            background-color: #f9f9f9;
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

                # Import cost data
                from utils.cost_data import get_monthly_costs, get_one_off_costs

                # Calculate detailed costs
                detailed_costs = {}
                
                # Get HD costs
                hd_costs = get_monthly_costs('hd')
                detailed_costs['hd'] = {}
                
                # Adjust for user inputs
                if caregiver_type != t['hired_caregiver']:
                    hd_costs.pop('ค่าจ้างผู้ดูแล', None)
                
                # Override travel and food costs if user provided them
                if travel_cost > 0:
                    hd_costs['ค่าเดินทาง ไป-กลับ'] = travel_cost * visits_per_month
                
                if food_cost > 0:
                    hd_costs['ค่าอาหาร/เครื่องดื่ม/ขนม'] = food_cost * visits_per_month
                
                # No income effects - Opportunity costs are removed
                hd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย', None)
                hd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของญาติ', None)
                
                # Add insurance coverage effects
                if coverage_factor > 0:
                    detailed_costs['hd'][t['cost_items']['insurance_copay']] = 30000 * coverage_factor
                
                # Add all remaining HD costs to the detailed costs
                for cost_name, cost_value in hd_costs.items():
                    detailed_costs['hd'][cost_name] = cost_value
                
                # Get PD (CAPD) costs
                pd_costs = get_monthly_costs('pd')
                detailed_costs['pd'] = {}
                
                # Adjust for user inputs
                if caregiver_type != t['hired_caregiver']:
                    pd_costs.pop('ค่าจ้างผู้ดูแล', None)
                
                # No income effects - Opportunity costs are removed
                pd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย', None)
                pd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของญาติ', None)
                
                # Home modification costs for PD
                pd_one_off = get_one_off_costs('pd')
                if all([home_clean, home_sink, home_space, home_private]):
                    pd_one_off.pop('Home modification cost', None)
                else:
                    detailed_costs['pd'][t['cost_items']['home_modification']] = pd_one_off.get('Home modification cost', 0)
                
                # Add insurance coverage effects
                if coverage_factor > 0:
                    detailed_costs['pd'][t['cost_items']['insurance_copay']] = 25000 * coverage_factor
                
                # Add all remaining PD costs to the detailed costs
                for cost_name, cost_value in pd_costs.items():
                    detailed_costs['pd'][cost_name] = cost_value
                
                # Get APD costs
                apd_costs = get_monthly_costs('apd')
                detailed_costs['apd'] = {}
                
                # Adjust for user inputs
                if caregiver_type != t['hired_caregiver']:
                    apd_costs.pop('ค่าจ้างผู้ดูแล', None)
                
                # No income effects - Opportunity costs are removed
                apd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย', None)
                apd_costs.pop('รายได้ที่เสียเนื่องจากขาดงานของญาติ', None)
                
                # Home modification costs for APD
                apd_one_off = get_one_off_costs('apd')
                if all([home_clean, home_sink, home_space, home_private]):
                    apd_one_off.pop('Home modification cost', None)
                else:
                    detailed_costs['apd'][t['cost_items']['home_modification']] = apd_one_off.get('Home modification cost', 0)
                
                # Add insurance coverage effects
                if coverage_factor > 0:
                    detailed_costs['apd'][t['cost_items']['insurance_copay']] = 35000 * coverage_factor
                
                # Add all remaining APD costs to the detailed costs
                for cost_name, cost_value in apd_costs.items():
                    detailed_costs['apd'][cost_name] = cost_value
                
                # Get CCC costs - mostly one-off
                ccc_costs = {}
                detailed_costs['ccc'] = {}
                
                # Add palliative care monthly costs (estimated)
                detailed_costs['ccc'][t['cost_items']['base_cost']] = 15000 * coverage_factor
                detailed_costs['ccc'][t['cost_items']['medicine']] = 3000 * coverage_factor
                
                # Add caregiver costs if applicable
                if caregiver_type == t['hired_caregiver']:
                    detailed_costs['ccc'][t['cost_items']['caregiver']] = 8741  # Using HD caregiver cost as estimate
                
                # Add utilities costs for all treatment types
                for treatment in ['hd', 'pd', 'apd', 'ccc']:
                    # Check for Thai utilities keys and standardize them
                    utility_keys = ['ค่าสาธารณูปโภค', 'ค่าน้ำ/ไฟ', 'Utilities', 'utilities']
                    utility_cost = 0
                    
                    for key in utility_keys:
                        if key in detailed_costs[treatment]:
                            utility_cost += detailed_costs[treatment].pop(key, 0)
                    
                    if utility_cost > 0:
                        detailed_costs[treatment][t['cost_items']['utilities']] = utility_cost

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
                    <h3 style='color: {treatment_colors[treatment]}; margin-bottom: 8px;'>{t['treatment_types'][treatment]}</h3>
                    <div style='font-size: 1.5rem; font-weight: 600; color: #2c3e50; margin-bottom: 3px;'>
                        ฿{st.session_state.monthly_totals[treatment]:,}
                    </div>
                    <div style='font-size: 0.8rem; color: #7f8c8d; margin-bottom: 5px;'>{t['per_month']}</div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(t['see_details']):
                    st.markdown("<div class='cost-breakdown'>", unsafe_allow_html=True)
                    for item, cost in st.session_state.detailed_costs[treatment].items():
                        if cost > 0:
                            st.markdown(f"• {item}: <b>฿{int(cost):,}</b>", unsafe_allow_html=True)
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
        <table class="dataframe" style="margin: 0.5rem 0; border-spacing: 0;">
            <thead>
                <tr>
                    <th style="padding: 10px 12px;">{t['time_period']}</th>
                    <th style="background-color: #1e88e5; padding: 10px 12px;">HD</th>
                    <th style="background-color: #26a69a; padding: 10px 12px;">PD</th>
                    <th style="background-color: #7e57c2; padding: 10px 12px;">APD</th>
                    <th style="background-color: #ef5350; padding: 10px 12px;">CCC</th>
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
        """
        
        # Print button script for the yearly projection table
        html_table += f"""
        <script>
        function printProjections() {{
          const projectionTable = document.querySelector('.dataframe').outerHTML;
          const title = "<h2 style='text-align:center;'>{t['yearly_projections']}</h2>";
          const printWindow = window.open('', '_blank');
          printWindow.document.write('<html><head><title>{t['yearly_projections']}</title>');
          printWindow.document.write('<style>body {{ font-family: Arial, sans-serif; }} table {{ width: 100%; border-collapse: collapse; }} th {{ background-color: #1e88e5; color: white; text-align: left; padding: 12px; }} td {{ padding: 10px; border-bottom: 1px solid #ddd; }} tr:nth-child(even) {{ background-color: #f2f2f2; }}</style>');
          printWindow.document.write('</head><body>');
          printWindow.document.write(title);
          printWindow.document.write(projectionTable);
          printWindow.document.write('</body></html>');
          printWindow.document.close();
          printWindow.print();
        }}
        </script>
        </div>
        """

        st.markdown(html_table, unsafe_allow_html=True)

        # Action buttons for print and start over
        st.markdown("<div class='section-container'>", unsafe_allow_html=True)
        cols = st.columns([1, 3, 1])
        with cols[1]:
            # Print yearly projections button
            st.markdown(f"""
            <button onclick="printProjections()" style="width: 100%; margin-bottom: 15px; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">{t['print']}</button>
            """, unsafe_allow_html=True)
            
            # Create a more prominent Start Over button with confirmation dialog
            start_over_clicked = st.button(
                t['start_over'], 
                use_container_width=True,
                key="start_over_button",
                help="This will reset all your inputs and calculations"
            )
            
            # Add confirmation dialog for Start Over
            if start_over_clicked:
                confirm = st.warning(
                    f"⚠️ {t['confirm_reset']}", 
                    icon="⚠️"
                )
                confirm_cols = st.columns([1, 1])
                with confirm_cols[0]:
                    if st.button("✅ Yes, start over", use_container_width=True):
                        st.session_state.clear()
                        st.rerun()
                with confirm_cols[1]:
                    if st.button("❌ No, cancel", use_container_width=True):
                        st.rerun()
                        
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