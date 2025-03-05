import streamlit as st
from utils.map_utils import calculate_distance
import folium
from streamlit_folium import folium_static

class QuestionFlow:
    def __init__(self):
        self.questions = self._initialize_questions()

    def _initialize_questions(self):
        return {
            0: self._employment_status,
            1: self._work_impact,
            2: self._income,
            3: self._caregiver_needs,
            4: self._caregiver_details,
            5: self._home_suitability,
            6: self._travel_costs,
            7: self._location_details,
            8: self._transportation_mode
        }

    def show_question(self):
        current_step = st.session_state.current_step
        if current_step < len(self.questions):
            self.questions[current_step]()
        else:
            st.session_state.show_comparison = True

    def _employment_status(self):
        st.subheader("Employment Status")
        employment = st.radio(
            "Are you currently working?",
            options=["Yes", "No"],
            key="employment"
        )
        self._next_button("employment")

    def _work_impact(self):
        if st.session_state.answers.get("employment") == "Yes":
            st.subheader("Impact on Work")
            impact = st.radio(
                "If you start dialysis, how will it affect your ability to work?",
                options=[
                    "I will have to leave my job entirely",
                    "I will be able to work, just not during dialysis",
                    "Dialysis will not affect how much I get paid"
                ],
                key="work_impact"
            )
        self._next_button("work_impact")

    def _income(self):
        st.subheader("Monthly Income")
        income = st.number_input(
            "Please enter your monthly income (THB):",
            min_value=0,
            value=0,
            step=1000,
            key="income"
        )
        self._next_button("income")

    def _caregiver_needs(self):
        st.subheader("Caregiver Requirements")
        needs = st.radio(
            "Do you require the assistance of a caregiver?",
            options=[
                "I am able to help myself in all daily life routines",
                "I require assistance to travel outside",
                "I require assistance for daily life routines"
            ],
            key="caregiver_needs"
        )
        self._next_button("caregiver_needs")

    def _caregiver_details(self):
        if "require assistance" in st.session_state.answers.get("caregiver_needs", ""):
            st.subheader("Caregiver Details")
            st.text_input("Who will your caretaker be?", key="caregiver_name")
            st.number_input(
                "What is their monthly income? (THB)",
                min_value=0,
                step=1000,
                key="caregiver_income"
            )
            st.number_input(
                "Monthly payment to caregiver (THB)",
                min_value=0,
                step=1000,
                key="caregiver_payment"
            )
        self._next_button("caregiver_details")

    def _home_suitability(self):
        st.subheader("Home Suitability for PD")
        suitable = st.radio(
            "Is your home suitable for peritoneal dialysis (PD)?",
            options=["Yes", "No"],
            key="home_suitable"
        )

        if suitable == "Yes":
            st.checkbox("There is a clean, dust-free corner", key="clean_corner")
            st.checkbox("There is a sink for handwashing", key="has_sink")
            st.slider(
                "Home condition score",
                min_value=1,
                max_value=10,
                value=5,
                key="home_score"
            )
        self._next_button("home_suitability")

    def _travel_costs(self):
        st.subheader("Travel Costs")
        knows_cost = st.radio(
            "Do you know how much it costs to travel to your nearest dialysis center?",
            options=["Yes", "No"],
            key="knows_travel_cost"
        )

        if knows_cost == "Yes":
            st.number_input(
                "Cost per visit (THB)",
                min_value=0,
                step=10,
                key="travel_cost"
            )
        self._next_button("travel_costs")

    def _location_details(self):
        st.subheader("Location Details")

        # Create a folium map centered on Thailand
        m = folium.Map(location=[13.7563, 100.5018], zoom_start=6)

        st.write("Select your home location:")
        folium_static(m)

        st.write("Select dialysis center location:")
        folium_static(m)

        # For demo purposes, we'll use text inputs
        st.number_input(
            "Distance to center (km)",
            min_value=0,
            step=1,
            key="distance"
        )
        self._next_button("location_details")

    def _transportation_mode(self):
        st.subheader("Transportation Mode")
        mode = st.selectbox(
            "How do you plan to travel to the dialysis center?",
            options=["Car", "Public Transportation", "Taxi", "Ambulance"],
            key="transport_mode"
        )
        self._next_button("transportation_mode")

    def _next_button(self, key):
        if st.button("Next"):
            st.session_state.answers[key] = st.session_state[key]
            st.session_state.current_step += 1
            st.rerun()