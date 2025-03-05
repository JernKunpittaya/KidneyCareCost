import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.translations import TRANSLATIONS

# Page configuration
st.set_page_config(
    page_title="Kidney Dialysis Cost Calculator",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="collapsed"  # Better for mobile
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

# Get translations for current language
t = TRANSLATIONS[st.session_state.language]

# Title
st.title(t['title'])
st.markdown(t['subtitle'])

# Only show form if not showing results
if not st.session_state.show_results:
    with st.form("cost_calculator"):
        # Basic information
        st.subheader(t['basic_info'])
        employment = st.radio(t['employment'], [t['yes'], t['no']])

        # Work impact question (shown only if employed)
        work_impact = None
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

        # Medical Information
        st.subheader(t['medical_info'])
        medical_conditions = st.multiselect(
            t['select_conditions'],
            [t['diabetes'], t['hypertension'], t['heart_disease'], t['none']],
            default=[t['none']]
        )

        # Care needs
        st.subheader(t['care_requirements'])
        care_needs = st.radio(
            t['assistance_needs'],
            [
                t['no_assistance'],
                t['travel_assistance'],
                t['daily_assistance']
            ]
        )

        # Caregiver details
        if care_needs != t['no_assistance']:
            st.subheader(t['caregiver_details'])
            caregiver_income = st.number_input(
                t['caregiver_income'],
                min_value=0,
                value=0,
                step=1000
            )

        # Home Assessment
        st.subheader(t['home_assessment'])
        home_suitable = st.radio(
            t['pd_suitability'],
            [t['yes'], t['no']]
        )

        utilities_cost = st.number_input(
            t['utilities_cost'],
            min_value=0,
            value=0,
            step=100
        )

        # Travel information
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

        # Submit button
        submitted = st.form_submit_button(t['calculate'])

        if submitted:
            # Calculate income loss based on work impact
            income_loss_factor = {
                t['leave_job']: 1.0,  # 100% income loss
                t['work_during_dialysis']: 0.3,  # 30% income loss
                t['no_income_effect']: 0.0  # No income loss
            }

            # Calculate detailed costs
            detailed_costs = {
                'apd': {
                    'accounting': {
                        'base_cost': 30000,
                        'utilities': utilities_cost,
                        'caregiver': 0 if care_needs == t['no_assistance'] else 15000
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == t['no_assistance'] else (caregiver_income * 0.1),
                        'patient_lost_income': monthly_income * (income_loss_factor.get(work_impact, 0) if employment == t['yes'] else 0)
                    }
                },
                'capd': {
                    'accounting': {
                        'base_cost': 25000,
                        'caregiver': 0 if care_needs == t['no_assistance'] else 15000
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == t['no_assistance'] else (caregiver_income * 0.15),
                        'patient_lost_income': monthly_income * (income_loss_factor.get(work_impact, 0) if employment == t['yes'] else 0)
                    }
                },
                'hd': {
                    'accounting': {
                        'base_cost': 30000,
                        'travel': travel_cost * 13,  # 13 visits per month
                        'caregiver': 0 if care_needs == t['no_assistance'] else 15000,
                        'food': food_cost * 13  # 13 visits per month
                    },
                    'opportunity': {
                        'caregiver_lost_income': 0 if care_needs == t['no_assistance'] else (caregiver_income * 0.3),
                        'patient_lost_income': monthly_income * (income_loss_factor.get(work_impact, 0) if employment == t['yes'] else 0)
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

def create_cost_comparison_chart(costs, labels):
    """Create a bar chart comparing costs between treatments"""
    fig = go.Figure(data=[
        go.Bar(
            x=list(costs.keys()),
            y=list(costs.values()),
            text=[f"฿{cost:,.0f}" for cost in costs.values()],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title=labels['title'],
        xaxis_title=labels['xaxis'],
        yaxis_title=labels['yaxis'],
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def create_cost_breakdown_chart(costs, treatment, labels):
    """Create a pie chart showing cost breakdown for a treatment"""
    values = []
    labels_list = []

    # Combine all costs
    all_costs = {}
    all_costs.update(costs[treatment]['accounting'])
    all_costs.update(costs[treatment]['opportunity'])

    # Filter out zero values
    for key, value in all_costs.items():
        if value > 0:
            values.append(value)
            labels_list.append(labels[key])

    fig = go.Figure(data=[go.Pie(
        labels=labels_list,
        values=values,
        hole=.4,
        textinfo='percent+label'
    )])

    fig.update_layout(
        height=300,
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

# Show results if calculation is done
if st.session_state.show_results:
    st.header(t['cost_comparison'])

    # Monthly cost comparison chart
    monthly_chart = create_cost_comparison_chart(
        st.session_state.monthly_totals,
        {
            'title': t['monthly_overview'],
            'xaxis': 'Treatment Type',
            'yaxis': 'Monthly Cost (THB)'
        }
    )
    st.plotly_chart(monthly_chart, use_container_width=True)

    # Detailed breakdown for each treatment
    st.subheader(t['monthly_overview'])

    # Use tabs for better mobile experience
    tab1, tab2, tab3 = st.tabs(["APD", "CAPD", "HD"])

    with tab1:
        st.metric("APD", f"฿{st.session_state.monthly_totals['apd']:,.2f}")
        breakdown_chart_apd = create_cost_breakdown_chart(
            st.session_state.detailed_costs,
            'apd',
            t
        )
        st.plotly_chart(breakdown_chart_apd, use_container_width=True)
        with st.expander(t['see_details']):
            st.markdown(f"### {t['accounting_costs']}")
            for key, value in st.session_state.detailed_costs['apd']['accounting'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")
            st.markdown(f"### {t['opportunity_costs']}")
            for key, value in st.session_state.detailed_costs['apd']['opportunity'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")

    with tab2:
        st.metric("CAPD", f"฿{st.session_state.monthly_totals['capd']:,.2f}")
        breakdown_chart_capd = create_cost_breakdown_chart(
            st.session_state.detailed_costs,
            'capd',
            t
        )
        st.plotly_chart(breakdown_chart_capd, use_container_width=True)
        with st.expander(t['see_details']):
            st.markdown(f"### {t['accounting_costs']}")
            for key, value in st.session_state.detailed_costs['capd']['accounting'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")
            st.markdown(f"### {t['opportunity_costs']}")
            for key, value in st.session_state.detailed_costs['capd']['opportunity'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")

    with tab3:
        st.metric("HD", f"฿{st.session_state.monthly_totals['hd']:,.2f}")
        breakdown_chart_hd = create_cost_breakdown_chart(
            st.session_state.detailed_costs,
            'hd',
            t
        )
        st.plotly_chart(breakdown_chart_hd, use_container_width=True)
        with st.expander(t['see_details']):
            st.markdown(f"### {t['accounting_costs']}")
            for key, value in st.session_state.detailed_costs['hd']['accounting'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")
            st.markdown(f"### {t['opportunity_costs']}")
            for key, value in st.session_state.detailed_costs['hd']['opportunity'].items():
                st.markdown(f"- {t[key]}: ฿{value:,.2f}")

    # Long-term projections visualization
    st.subheader(t['long_term_projections'])
    projections_data = {
        'APD': [
            st.session_state.yearly_costs['apd']['1_year'],
            st.session_state.yearly_costs['apd']['5_years'],
            st.session_state.yearly_costs['apd']['10_years']
        ],
        'CAPD': [
            st.session_state.yearly_costs['capd']['1_year'],
            st.session_state.yearly_costs['capd']['5_years'],
            st.session_state.yearly_costs['capd']['10_years']
        ],
        'HD': [
            st.session_state.yearly_costs['hd']['1_year'],
            st.session_state.yearly_costs['hd']['5_years'],
            st.session_state.yearly_costs['hd']['10_years']
        ]
    }

    fig = go.Figure()
    x_axis = ['1 Year', '5 Years', '10 Years']

    for treatment in projections_data:
        fig.add_trace(go.Bar(
            name=treatment,
            x=x_axis,
            y=projections_data[treatment],
            text=[f"฿{cost:,.0f}" for cost in projections_data[treatment]],
            textposition='auto',
        ))

    fig.update_layout(
        barmode='group',
        height=400,
        margin=dict(t=30, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)

    # Table view (collapsible for mobile)
    with st.expander(t['yearly_projections']):
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

    if st.button(t['start_over']):
        st.session_state.show_results = False
        st.rerun()

    # Footer with notes
    st.markdown("---")
    st.markdown(f"**{t['notes']}:**")
    st.markdown(t['costs_may_vary'])
    st.markdown(t['inflation_note'])
    st.markdown(t['consult_note'])