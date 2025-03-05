def calculate_costs(answers):
    """Calculate monthly costs for each treatment option."""
    
    # Base costs (THB per month)
    BASE_COSTS = {
        'hd': 30000,  # Hemodialysis
        'pd': 25000,  # Peritoneal Dialysis
        'palliative': 15000  # Palliative Care
    }
    
    # Calculate travel costs for HD
    travel_cost = 0
    if answers.get('travel_cost'):
        travel_cost = float(answers['travel_cost']) * 13  # Assuming 13 visits per month
    
    # Calculate caregiver costs
    caregiver_cost = 0
    if 'caregiver_payment' in answers:
        caregiver_cost = float(answers['caregiver_payment'])
    
    # Calculate lost income
    lost_income = 0
    if answers.get('work_impact') == "I will have to leave my job entirely":
        lost_income = float(answers.get('income', 0))
    elif answers.get('work_impact') == "I will be able to work, just not during dialysis":
        lost_income = float(answers.get('income', 0)) * 0.3  # Assuming 30% income loss
    
    # Calculate final costs
    costs = {
        'hd': BASE_COSTS['hd'] + travel_cost + caregiver_cost + lost_income,
        'pd': BASE_COSTS['pd'] + caregiver_cost + (lost_income * 0.5),  # PD has less impact on work
        'palliative': BASE_COSTS['palliative'] + caregiver_cost
    }
    
    return costs
