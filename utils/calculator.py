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
    
    # Calculate lost income with robust error handling
    lost_income = 0
    monthly_income = 0
    
    try:
        # Get income with safe conversion and default to 0
        if 'income' in answers and answers.get('income'):
            monthly_income = float(answers.get('income', 0))
        
        # Check if income was entered as lump sum and convert to monthly
        if answers.get('income_type') == "Lump sum payments" and 'annual_income' in answers:
            if answers.get('annual_income'):
                monthly_income = float(answers.get('annual_income', 0)) / 12
                
        # Calculate income loss based on work impact
        if answers.get('work_impact') == "I will have to leave my job entirely":
            lost_income = monthly_income
        elif answers.get('work_impact') == "I will be able to work, just not during dialysis":
            lost_income = monthly_income * 0.3  # Assuming 30% income loss
            
    except (ValueError, TypeError) as e:
        # Handle any conversion errors gracefully
        lost_income = 0  # Default to zero on error
    
    # Calculate final costs
    costs = {
        'hd': BASE_COSTS['hd'] + travel_cost + caregiver_cost + lost_income,
        'pd': BASE_COSTS['pd'] + caregiver_cost + (lost_income * 0.5),  # PD has less impact on work
        'palliative': BASE_COSTS['palliative'] + caregiver_cost
    }
    
    return costs
