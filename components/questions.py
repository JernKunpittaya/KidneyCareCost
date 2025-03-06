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
        st.info("Your employment status helps us estimate how dialysis treatment might affect your income.")
        employment = st.radio(
            "Are you currently working?",
            options=["Yes", "No"],
            key="employment"
        )
        self._next_button("employment")

    def _work_impact(self):
        if st.session_state.answers.get("employment") == "Yes":
            st.subheader("Impact on Work")
            st.info("Hemodialysis typically requires 3-4 hours per session, 2-3 times per week. Peritoneal dialysis can be done at home with more flexible scheduling.")
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
        
        # Add explanatory note
        st.info("This information helps us calculate potential income loss due to treatment. All data remains private.")
        
        income_type = st.radio(
            "How do you receive your income?",
            options=["Monthly salary", "Lump sum payments", "No income"],
            key="income_type"
        )
        
        if income_type == "Monthly salary":
            income = st.number_input(
                "Please enter your monthly income (THB):",
                min_value=0,
                value=0,
                step=1000,
                key="income"
            )
        elif income_type == "Lump sum payments":
            annual_income = st.number_input(
                "Please enter your annual income (THB):",
                min_value=0,
                value=0,
                step=10000,
                key="annual_income"
            )
            # Convert lump sum to monthly equivalent
            if "annual_income" in st.session_state:
                st.session_state.income = st.session_state.annual_income / 12
                st.info(f"Your estimated monthly income: ฿{st.session_state.income:,.2f}")
        else:
            st.session_state.income = 0
            
        self._next_button("income")

    def _caregiver_needs(self):
        st.subheader("Caregiver Requirements")
        st.info("Different treatments require different levels of assistance. This helps us estimate potential caregiver costs.")
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
        if "require assistance" in st.session_state.get("caregiver_needs", ""):
            st.subheader("Caregiver Details")

            # Store individual caregiver fields
            caregiver_name = st.text_input("Who will your caretaker be?", key="caregiver_name")
            caregiver_income = st.number_input(
                "What is their monthly income? (THB)",
                min_value=0,
                step=1000,
                key="caregiver_income"
            )
            caregiver_payment = st.number_input(
                "Monthly payment to caregiver (THB)",
                min_value=0,
                step=1000,
                key="caregiver_payment"
            )

            # Store all caregiver details in a dictionary
            caregiver_info = {
                "name": caregiver_name,
                "income": caregiver_income,
                "payment": caregiver_payment
            }

            if st.button("Next"):
                # Store individual fields in answers
                st.session_state.answers["caregiver_name"] = caregiver_name
                st.session_state.answers["caregiver_income"] = caregiver_income
                st.session_state.answers["caregiver_payment"] = caregiver_payment
                st.session_state.current_step += 1
                st.rerun()
        else:
            # Skip caregiver details if no assistance needed
            st.session_state.current_step += 1
            st.rerun()

    def _home_suitability(self):
        st.subheader("Home Suitability for PD")
        st.info("Peritoneal dialysis (PD) requires a clean environment and basic amenities at home. This helps determine if your home is suitable for PD treatment.")
        suitable = st.radio(
            "Is your home suitable for peritoneal dialysis (PD)?",
            options=["Yes", "No"],
            key="home_suitable"
        )

        if suitable == "Yes":
            st.checkbox("There is a clean, dust-free corner", key="clean_corner", help="PD requires a clean area to reduce infection risk")
            st.checkbox("There is a sink for handwashing", key="has_sink", help="Proper hand hygiene is essential for PD")
            st.slider(
                "Home condition score",
                min_value=1,
                max_value=10,
                value=5,
                key="home_score",
                help="1 = Poor conditions, 10 = Excellent conditions"
            )
        self._next_button("home_suitability")

    def _travel_costs(self):
        st.subheader("Travel Costs")
        st.info("Hemodialysis typically requires 2-3 trips to a dialysis center per week. Travel costs can be significant over time.")
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
                key="travel_cost",
                help="Include round-trip costs (e.g., gas, taxi, public transport)"
            )
        else:
            st.info("We'll estimate travel costs based on your location information in the next step.")
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
            if key in st.session_state:
                st.session_state.answers[key] = st.session_state[key]
                st.session_state.current_step += 1
                st.rerun()