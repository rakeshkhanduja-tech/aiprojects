from datetime import date, timedelta
import random

def run_seed(db_manager):
    # Seed Users
    users = [
        ("Alice Johnson", "Senior Sales Rep", "North America"),
        ("Bob Smith", "Account Executive", "EMEA"),
        ("Charlie Davis", "Sales Manager", "APAC")
    ]
    for name, role, region in users:
        db_manager.execute(
            "INSERT INTO users (name, role, region) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (name, role, region)
        )

    # Seed Customers
    customers = [
        ("TechCorp Solution", "Software", 0.1, "North America"),
        ("Global Logistics Inc", "Transportation", 0.8, "EMEA"), # Risky customer
        ("Starlight Energy", "Energy", 0.3, "APAC"),
        ("EcoBuild Ltd", "Construction", 0.2, "North America")
    ]
    for name, industry, risk, region in customers:
        db_manager.execute(
            "INSERT INTO customers (name, industry, risk_score, region) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (name, industry, risk, region)
        )

    # Get IDs for foreign keys
    user_ids = [r['id'] for r in db_manager.query("SELECT id FROM users")]
    customer_ids = [r['id'] for r in db_manager.query("SELECT id FROM customers")]

    # Seed Deals
    deals = [
        (customer_ids[0], user_ids[0], 50000.0, "Closing", 0.9, date.today() + timedelta(days=5)),
        (customer_ids[1], user_ids[1], 120000.0, "Negotiation", 0.4, date.today() + timedelta(days=45)), # Stalled deal
        (customer_ids[2], user_ids[2], 75000.0, "Discovery", 0.2, date.today() + timedelta(days=90)),
        (customer_ids[3], user_ids[0], 30000.0, "Proposal", 0.6, date.today() + timedelta(days=20))
    ]
    for cust_id, owner_id, val, stage, prob, close_date in deals:
        db_manager.execute(
            "INSERT INTO deals (customer_id, owner_id, deal_value, stage, probability, expected_close_date) VALUES (%s, %s, %s, %s, %s, %s)",
            (cust_id, owner_id, val, stage, prob, close_date)
        )

    # Seed Activities
    deal_ids = [r['id'] for r in db_manager.query("SELECT id FROM deals")]
    activities = [
        (deal_ids[0], "Call", "Client ready to sign pending final approval."),
        (deal_ids[1], "Email", "Client hasn't responded in 10 days regarding the contract."),
        (deal_ids[2], "Meeting", "Deep dive into technical requirements."),
        (deal_ids[3], "Proposal", "Sent updated pricing proposal.")
    ]
    for deal_id, a_type, notes in activities:
        db_manager.execute(
            "INSERT INTO activities (deal_id, activity_type, notes) VALUES (%s, %s, %s)",
            (deal_id, a_type, notes)
        )

    # Seed Policies
    policies = [
        ("Discount Policy", "Deals over $100k require Manager approval for discounts > 10%."),
        ("Follow-up Policy", "Active deals must have a recorded activity within the last 7 days."),
        ("Risk Policy", "Customers with risk_score > 0.7 must be reviewed by Compliance.")
    ]
    for name, rule in policies:
        db_manager.execute(
            "INSERT INTO policies (policy_name, rule) VALUES (%s, %s)",
            (name, rule)
        )
