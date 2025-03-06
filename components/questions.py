
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
        st.info("Your employment status helps us estimate how dialysis treatment might affect your income and treatment schedule flexibility.")
        employment = st.radio(
            "Are you currently working?",
            options=["Yes", "No"],
            key="employment"
        )
        self._next_button("employment")

    def _work_impact(self):
        if st.session_state.answers.get("employment") == "Yes":
            st.subheader("Impact on Work")
            st.info("Different dialysis treatments have different impacts on your work schedule:\n- Hemodialysis typically requires 3-4 hours per session, 2-3 times per week at a medical facility\n- Peritoneal dialysis can be done at home with more flexible scheduling, including overnight options")
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
        
        # Add detailed explanatory note
        st.info("This information helps us calculate potential income loss due to treatment. Different treatment options may affect your work capacity differently. All financial information remains private and is only used for cost calculation.")
        
        st.info("💡 **Income Information**: Different income types are handled differently to calculate treatment costs correctly. We need this information to properly estimate potential income loss during treatment.")
        
        income_type = st.radio(
            "How do you receive your income?",
            options=["Monthly salary", "Lump sum payments", "No income"],
            key="income_type",
            help="Select how you typically receive payment for your work"
        )
        
        if income_type == "Monthly salary":
            income = st.number_input(
                "Please enter your monthly income (THB):",
                min_value=0,
                value=0,
                step=1000,
                key="income",
                help="Enter your typical monthly income before taxes and deductions"
            )
            if income > 0:
                st.success(f"✅ Monthly income entered: ฿{income:,.2f}")
        elif income_type == "Lump sum payments":
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <p><strong>About Lump Sum Payments:</strong> This includes seasonal work, contract work, freelancing, or annual bonuses.</p>
                <p>We'll convert your annual income to a monthly equivalent to calculate treatment impacts.</p>
            </div>
            """, unsafe_allow_html=True)
            
            annual_income = st.number_input(
                "Please enter your annual income (THB):",
                min_value=0,
                value=0,
                step=10000,
                key="annual_income",
                help="Enter your estimated total annual income from all sources"
            )
            # Convert lump sum to monthly equivalent
            if "annual_income" in st.session_state and st.session_state.annual_income > 0:
                st.session_state.income = st.session_state.annual_income / 12
                st.success(f"✅ Your estimated monthly income: ฿{st.session_state.income:,.2f}")
                st.info("How we calculate this: Annual income ÷ 12 = Monthly income")
                
                # Show bilingual explanation
                st.markdown("""
                <div style="background-color: #fff8e1; padding: 10px; border-radius: 5px;">
                    <p><strong>🇬🇧 Lump Sum Calculation:</strong> We divide your annual income by 12 to estimate monthly income for treatment impact calculations.</p>
                    <p><strong>🇹🇭 วิธีคำนวณรายได้แบบเหมาจ่าย:</strong> เราแบ่งรายได้ทั้งปีของคุณด้วย 12 เพื่อประมาณการรายได้ต่อเดือน เพื่อคำนวณผลกระทบด้านการเงินระหว่างการรักษา</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.session_state.income = 0
            st.info("No income selected. We'll calculate costs without considering income loss.")
        else:
            st.session_state.income = 0
            
        self._next_button("income")

    def _caregiver_needs(self):
        st.subheader("Caregiver Requirements")
        st.info("Different treatments require different levels of assistance:\n- Hemodialysis: You'll need help traveling to/from clinics 2-3 times weekly\n- Peritoneal Dialysis: You may need assistance with equipment setup and daily exchanges\n- All options: Assistance needs may increase over time")
        needs = st.radio(
            "Do you require the assistance of a caregiver?",
            options=[
                "I am able to help myself in all daily life routines",
                "I require assistance to travel outside",
                "I require assistance for daily life routines"
            ],
            key="caregiver_needs",
            help="Consider your current mobility and how it might change with dialysis"
        )
        self._next_button("caregiver_needs")

    def _caregiver_details(self):
        if "require assistance" in st.session_state.get("caregiver_needs", ""):
            st.subheader("Caregiver Details")
            st.info("Caregiver costs can significantly impact your total treatment expenses. This information helps us provide a more accurate cost estimate.")

            # Store individual caregiver fields
            caregiver_name = st.text_input(
                "Who will your caretaker be?", 
                key="caregiver_name",
                help="Family member, friend, or professional caregiver"
            )
            caregiver_income = st.number_input(
                "What is their monthly income? (THB)",
                min_value=0,
                step=1000,
                key="caregiver_income",
                help="If a family member will reduce work hours to care for you, this helps calculate opportunity costs"
            )
            caregiver_payment = st.number_input(
                "Monthly payment to caregiver (THB)",
                min_value=0,
                step=1000,
                key="caregiver_payment",
                help="Amount you expect to pay for caregiving services per month"
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
        st.info("Peritoneal dialysis (PD) requires:\n- Clean environment to prevent infection\n- Storage space for supplies (boxes of solution bags)\n- Access to running water and electricity\n- Space for equipment\n\nYour home assessment helps determine if PD is a viable option for you.")
        st.warning("If your home doesn't meet cleanliness requirements, you may need to spend additional money (approximately ฿5,000) on home modifications or consider center-based treatment instead.")
        suitable = st.radio(
            "Is your home suitable for peritoneal dialysis (PD)?",
            options=["Yes", "No"],
            key="home_suitable",
            help="If uncertain, select 'Yes' and answer the follow-up questions"
        )

        if suitable == "Yes":
            st.checkbox("There is a clean, dust-free corner", key="clean_corner", help="PD requires a clean area to reduce infection risk. Infections can lead to additional medical costs and hospitalization.")
            st.checkbox("There is a sink for handwashing", key="has_sink", help="Proper hand hygiene is essential for PD to prevent infection. Without this, home-based PD may not be safe.")
            st.checkbox("There is adequate storage space for supplies", key="has_storage", help="PD requires storage for solution bags (typically 20-30 bags per week) and equipment. Inadequate storage may require home modifications.")
            st.checkbox("There is a private space for treatment", key="has_private", help="Privacy during exchanges is important for comfort and hygiene.")
            st.slider(
                "Home condition score",
                min_value=1,
                max_value=10,
                value=5,
                key="home_score",
                help="1 = Poor conditions (additional costs for modification likely), 10 = Excellent conditions (no modifications needed)"
            )
        self._next_button("home_suitability")

    def _travel_costs(self):
        st.subheader("Travel Costs")
        
        # Improved travel costs explanation with bilingual support
        st.markdown("""
        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 15px;">
            <h4 style="margin-top: 0;">📍 Travel Cost Impact</h4>
            <p><strong>Hemodialysis requires 2-3 visits per week</strong> to a dialysis center, which means:</p>
            <ul>
                <li>8-13 trips per month</li>
                <li>Transportation costs (fuel, taxi, public transport)</li>
                <li>Food expenses during treatment days</li>
                <li>Potential accommodation costs if the center is far away</li>
            </ul>
            <p>These recurring costs significantly impact your total treatment expenses.</p>
            <hr style="border-top: 1px dashed #ccc; margin: 10px 0;">
            <p><strong>🇹🇭 การฟอกไตต้องเดินทางไปโรงพยาบาลหรือศูนย์ฟอกไต 2-3 ครั้งต่อสัปดาห์</strong> ซึ่งหมายถึง:</p>
            <ul>
                <li>ต้องเดินทาง 8-13 ครั้งต่อเดือน</li>
                <li>มีค่าเดินทาง (น้ำมัน, แท็กซี่, รถสาธารณะ)</li>
                <li>ค่าอาหารในวันที่รับการรักษา</li>
                <li>อาจมีค่าที่พักถ้าศูนย์ฟอกไตอยู่ไกล</li>
            </ul>
            <p>ค่าใช้จ่ายเหล่านี้ส่งผลกระทบอย่างมากต่อค่าใช้จ่ายในการรักษาโดยรวม</p>
        </div>
        """, unsafe_allow_html=True)
        
        knows_cost = st.radio(
            "Do you know how much it costs to travel to your nearest dialysis center?",
            options=["Yes", "No"],
            key="knows_travel_cost",
            help="Consider transportation, food, and any other expenses per visit"
        )

        if knows_cost == "Yes":
            cost = st.number_input(
                "Cost per visit (THB)",
                min_value=0,
                step=10,
                key="travel_cost",
                help="Include round-trip costs (e.g., gas, taxi, public transport)"
            )
            
            if cost > 0:
                # Show multiplication example to help user understand total impact
                visits_per_month = 13  # Assuming worst case
                monthly_cost = cost * visits_per_month
                
                st.success(f"✅ Cost entered: ฿{cost:,.2f} per visit")
                st.info(f"📊 Estimated monthly travel cost: ฿{cost:,.2f} × {visits_per_month} visits = ฿{monthly_cost:,.2f}")
        else:
            st.info("👉 We'll estimate travel costs based on your location information in the next step.")
            
            # Add distance-based cost estimate hint
            st.markdown("""
            <div style="background-color: #fff8e1; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <p><strong>💡 Travel Cost Estimate:</strong> If you're not sure, think about your travel mode:</p>
                <ul>
                    <li>Public transport: Typically ฿30-100 per trip</li>
                    <li>Car: ~฿5-8 per km for fuel + parking</li>
                    <li>Taxi: ~฿40 base fare + ฿5-8 per km</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        self._next_button("travel_costs")

    def _location_details(self):
        st.subheader("Location Details")
        st.info("Your distance from dialysis centers affects travel time, costs, and frequency of visits. This information helps us calculate transportation expenses and assess the feasibility of different treatment options.")

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
            key="distance",
            help="Approximate one-way distance from your home to the nearest dialysis center"
        )
        self._next_button("location_details")

    def _transportation_mode(self):
        st.subheader("Transportation Mode")
        st.info("Your mode of transportation affects both cost and convenience:\n- Car: More comfortable but has fuel and parking costs\n- Public Transport: Less expensive but may be difficult if you feel unwell after treatment\n- Taxi: Convenient but more expensive\n- Ambulance: Available in some cases but costly without coverage")
        mode = st.selectbox(
            "How do you plan to travel to the dialysis center?",
            options=["Car", "Public Transportation", "Taxi", "Ambulance"],
            key="transport_mode",
            help="Select your most likely mode of transportation for treatment visits"
        )
        self._next_button("transportation_mode")

    def _next_button(self, key):
        if st.button("Next"):
            if key in st.session_state:
                st.session_state.answers[key] = st.session_state[key]
                st.session_state.current_step += 1
                st.rerun()
