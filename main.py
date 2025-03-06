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

# Import custom CSS
with open('assets/style.css', 'r') as f:
    css = f.read()
    
st.markdown(f"""
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap">
    <style>
    {css}
    
    .header-container {{
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, var(--primary-light), var(--primary-dark));
        border-radius: var(--border-radius);
        color: white;
    }}
    
    .header-container h1 {{
        color: white;
        margin-bottom: 0.5rem;
    }}
    
    .header-subtitle {{
        opacity: 0.9;
        font-weight: 300;
        font-size: 1.1rem;
    }}
    
    .section-header {{
        background-color: var(--primary-color);
        color: white;
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius);
        margin: 1.5rem 0 1rem 0;
        font-weight: 500;
    }}
    
    .footer {{
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(0,0,0,0.1);
        font-size: 0.9rem;
        opacity: 0.8;
    }}
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

# Title with custom container
st.markdown(f"""
<div class="header-container">
    <h1>{t['title']}</h1>
    <p class="header-subtitle">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.show_results:
    with st.form("cost_calculator"):
        # Insurance type
        st.markdown(f'<div class="section-header">{t["insurance_type"]}</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="section-header">{t["basic_info"]}</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="section-header">{t["caregiver_needs"]}</div>', unsafe_allow_html=True)
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
        st.markdown(f'<div class="section-header">{t["home_assessment"]}</div>', unsafe_allow_html=True)
        home_clean = st.checkbox(t['home_questions']['cleanliness'])
        home_sink = st.checkbox(t['home_questions']['sink'])
        home_space = st.checkbox(t['home_questions']['space'])
        home_private = st.checkbox(t['home_questions']['crowding'])

        # Treatment Frequency
        st.markdown(f'<div class="section-header">{t["treatment_frequency"]}</div>', unsafe_allow_html=True)
        hd_frequency = st.radio(
            t['hd_frequency'],
            [t['freq_2'], t['freq_3']]
        )

        # Travel Information
        st.markdown(f'<div class="section-header">{t["travel_info"]}</div>', unsafe_allow_html=True)
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
            # Base costs by insurance type (example values, adjust based on actual coverage)
            coverage_factors = {
                t['insurance_options']['gold_card']: 0.05,      # 5% of total cost
                t['insurance_options']['civil_servant']: 0.0,   # 0% of total cost
                t['insurance_options']['social_security']: 0.1, # 10% of total cost
                t['insurance_options']['private_insurance']: 0.2, # 20% of total cost
                t['insurance_options']['other']: 0.3           # 30% of total cost
            }

            coverage_factor = coverage_factors[insurance]
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

    # Monthly costs bar chart with improved styling
    fig = go.Figure(data=[
        go.Bar(
            x=[t['treatment_types'][k] for k in ['hd', 'pd', 'apd', 'ccc']],
            y=[st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']],
            text=[f"฿{cost:,.0f}" for cost in [st.session_state.monthly_totals[k] for k in ['hd', 'pd', 'apd', 'ccc']]],
            textposition='auto',
            marker_color=['#1976d2', '#26a69a', '#7986cb', '#9575cd'],
            hoverinfo='y+name',
        )
    ])

    fig.update_layout(
        title={
            'text': t['monthly_overview'],
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Roboto'}
        },
        yaxis_title='Monthly Cost (THB)',
        height=450,
        margin=dict(t=70, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)',
        font={'family': 'Roboto'},
        xaxis={'tickangle': 0, 'categoryorder': 'total descending'},
        yaxis={'gridcolor': 'rgba(0,0,0,0.05)'},
        hoverlabel={'bgcolor': 'white', 'font_size': 14, 'font_family': 'Roboto'},
        barmode='group'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Detailed breakdown for each treatment with enhanced cards
    st.markdown(f'<div class="section-header">{t["monthly_overview"]}</div>', unsafe_allow_html=True)
    cols = st.columns(4)

    treatment_info = {
        'hd': {
            'pros': [t.get('hd_pros', ['Professional supervision', 'Structured schedule', 'No home setup required'])],
            'cons': [t.get('hd_cons', ['Regular travel required', 'Time commitment', 'Higher cost'])]
        },
        'pd': {
            'pros': [t.get('pd_pros', ['Home-based treatment', 'More flexibility', 'Greater independence'])],
            'cons': [t.get('pd_cons', ['Requires storage space', 'Daily commitment', 'Risk of infection'])]
        },
        'apd': {
            'pros': [t.get('apd_pros', ['Overnight treatment', 'More daytime freedom', 'Less manual procedures'])],
            'cons': [t.get('apd_cons', ['Machine needed', 'Higher utility costs', 'Technical complexity'])]
        },
        'ccc': {
            'pros': [t.get('ccc_pros', ['Comfort-focused', 'Less invasive', 'Lower cost'])],
            'cons': [t.get('ccc_cons', ['Limited treatment', 'Requires support system', 'Progressive symptoms'])]
        }
    }

    for i, (treatment, label) in enumerate([
        ('hd', 'HD'), ('pd', 'PD'), ('apd', 'APD'), ('ccc', 'CCC')
    ]):
        with cols[i]:
            st.markdown(f"""
            <div class="treatment-card">
                <h3>{t['treatment_types'][treatment]}</h3>
                <div class="cost-metric">฿{st.session_state.monthly_totals[treatment]:,.0f}</div>
                <div class="pros-cons">
                    <h4>✓ {t.get('pros', 'Pros')}</h4>
                    <ul class="pros">
                        {''.join([f'<li>{item}</li>' for item in treatment_info[treatment]['pros'][0]])}
                    </ul>
                    <h4>✗ {t.get('cons', 'Cons')}</h4>
                    <ul class="cons">
                        {''.join([f'<li>{item}</li>' for item in treatment_info[treatment]['cons'][0]])}
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(t['see_details']):
                for item, cost in st.session_state.detailed_costs[treatment].items():
                    if cost > 0:
                        st.markdown(f"- **{item}**: ฿{cost:,.2f}")

    # Yearly projections with enhanced visuals
    st.markdown(f'<div class="section-header">{t["yearly_projections"]}</div>', unsafe_allow_html=True)
    
    # Create a line chart for yearly projections
    years = [1, 5, 10]
    fig = go.Figure()
    
    treatments = ['hd', 'pd', 'apd', 'ccc']
    colors = ['#1976d2', '#26a69a', '#7986cb', '#9575cd']
    
    for i, treatment in enumerate(treatments):
        values = [st.session_state.yearly_costs[treatment][k] for k in ['1_year', '5_years', '10_years']]
        fig.add_trace(go.Scatter(
            x=years, 
            y=values,
            mode='lines+markers',
            name=t['treatment_types'][treatment],
            line=dict(color=colors[i], width=3),
            marker=dict(size=10)
        ))
    
    fig.update_layout(
        title={
            'text': t['yearly_projections'],
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 18, 'color': '#2c3e50', 'family': 'Roboto'}
        },
        xaxis_title='Years',
        yaxis_title='Cumulative Cost (THB)',
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=70, b=30, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)',
        font={'family': 'Roboto'},
        xaxis={'tickvals': years, 'gridcolor': 'rgba(0,0,0,0.05)'},
        yaxis={'gridcolor': 'rgba(0,0,0,0.05)'},
        hoverlabel={'bgcolor': 'white', 'font_size': 14, 'font_family': 'Roboto'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    with st.expander(t['see_details']):
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

    # Enhanced footer notes
    st.markdown("""
    <div class="footer">
        <h4>📝 Notes</h4>
        <ul>
    """, unsafe_allow_html=True)
    st.markdown(f"<li>{t['costs_may_vary']}</li>", unsafe_allow_html=True)
    st.markdown(f"<li>{t['insurance_note']}</li>", unsafe_allow_html=True)
    st.markdown(f"<li>{t['consult_note']}</li>", unsafe_allow_html=True)
    st.markdown("""
        </ul>
        <p style="text-align: center; margin-top: 20px;">
            © 2025 Kidney Dialysis Cost Calculator | Developed with ❤️ by Replit
        </p>
    </div>
    """, unsafe_allow_html=True)