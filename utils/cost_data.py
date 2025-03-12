"""
Cost data for kidney dialysis treatments based on research data
"""

COST_DATA = {
    'hd': {
        'ค่าจ้างผู้ดูแล': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 8741},
        'ค่าอาหาร/เครื่องดื่ม/ขนม': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 1509},
        'ค่าเดินทาง ไป-กลับ': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 1916},
        'ค่าที่พัก': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 132.66},
        'รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 6634},
        'รายได้ที่เสียเนื่องจากขาดงานของญาติ': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 2079},
        'Lifetime cost paid by household with palliative care': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 25299}
    },
    'pd': {  # CAPD
        'ค่าจ้างผู้ดูแล': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 12049},
        'ค่าอาหาร/เครื่องดื่ม/ขนม': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 154},
        'ค่าเดินทาง ไป-กลับ': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 294},
        'รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 212},
        'รายได้ที่เสียเนื่องจากขาดงานของญาติ': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 108},
        'ค่าที่พัก': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 2.41},
        'Home modification cost': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 24769},
        'Lifetime cost paid by household with palliative care': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 25299}
    },
    'apd': {
        'ค่าจ้างผู้ดูแล': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 11277},
        'ค่าอาหาร/เครื่องดื่ม/ขนม': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 165},
        'ค่าเดินทาง ไป-กลับ': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 148},
        'Utilities': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 124},
        'รายได้ที่เสียเนื่องจากขาดงานของผู้ป่วย': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 212},
        'รายได้ที่เสียเนื่องจากขาดงานของญาติ': {'type': 'Opportunity', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 108},
        'ค่าที่พัก': {'type': 'Accounting', 'category': 'Complication', 'frequency': 'Monthly', 'mean': 2.41},
        'ค่าสาธารณูปโภค': {'type': 'Accounting', 'category': 'Maintenance', 'frequency': 'Monthly', 'mean': 500},
        'Home modification cost': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 17149},
        'Lifetime cost paid by household with palliative care': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 25299}
    },
    'ccc': {
        'Lifetime cost paid by household with palliative care': {'type': 'Accounting', 'category': 'One-off', 'frequency': 'One-off', 'mean': 25299}
    }
}

# Helper functions to get costs by type
def get_monthly_costs(treatment_type, include_opportunity=True, include_maintenance=True, include_complication=True):
    """Get all monthly costs for a specific treatment type"""
    monthly_costs = {}

    if treatment_type not in COST_DATA:
        return monthly_costs

    for cost_name, details in COST_DATA[treatment_type].items():
        if details['frequency'] != 'Monthly':
            continue

        # Filter by type if requested
        if not include_opportunity and details['type'] == 'Opportunity':
            continue

        # Filter by category if requested
        if not include_maintenance and details['category'] == 'Maintenance':
            continue

        if not include_complication and details['category'] == 'Complication':
            continue

        monthly_costs[cost_name] = details['mean']

    return monthly_costs

def get_one_off_costs(treatment_type):
    """Get all one-off costs for a specific treatment type"""
    one_off_costs = {}

    if treatment_type not in COST_DATA:
        return one_off_costs

    for cost_name, details in COST_DATA[treatment_type].items():
        if details['frequency'] == 'One-off':
            one_off_costs[cost_name] = details['mean']

    return one_off_costs


#This section is added to address the missing print button functionality.  This is a GUESS based on common practices.  The actual implementation would depend on the surrounding code.
def print_costs(treatment_type, t): #Assumed function to print the costs; needs 't' for translation data
    detailed_costs = get_monthly_costs(treatment_type)
    detailed_costs.update(get_one_off_costs(treatment_type))

    # Add utilities costs for all treatment types
    for treatment in ['hd', 'pd', 'apd', 'ccc']:
        # First check for the Thai key
        if 'ค่าสาธารณูปโภค' in detailed_costs[treatment]:
            # Map to the translated key
            utility_cost = detailed_costs[treatment].pop('ค่าสาธารณูปโภค', 0)
            if utility_cost > 0:
                detailed_costs[treatment][t['cost_items']['utilities']] = utility_cost
        # Also check for any untranslated "utilities" entries and translate them
        elif 'utilities' in detailed_costs[treatment]:
            utility_cost = detailed_costs[treatment].pop('utilities', 0)
            if utility_cost > 0:
                detailed_costs[treatment][t['cost_items']['utilities']] = utility_cost

    #Print the costs (replace with your actual printing logic)
    print(f"Costs for {treatment_type}: {detailed_costs}")

# Example usage (replace with your actual call and translation data)
t = {'cost_items': {'utilities': 'Utilities'}} #Example translation data
print_costs('apd', t)
print_costs('hd', t)