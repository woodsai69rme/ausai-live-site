"""
Stripe & Gumroad Webhook Simulator for AutoMonetize AI
Simulates real-time subscription checkouts, recurring billing, and MRR metrics updates.
"""

import os
import sys
import json
import time
import random
import datetime

TIERS = [
    {"name": "Starter Pro", "amount": 19.00, "interval": "month"},
    {"name": "Growth Suite", "amount": 49.00, "interval": "month"},
    {"name": "Scale Enterprise", "amount": 199.00, "interval": "month"},
    {"name": "Lifetime Founder Pass", "amount": 299.00, "interval": "one-time"}
]

DOMAINS = ["gmail.com", "outlook.com", "stripe.dev", "startup.io", "agency.ai", "creatorhub.net"]

def simulate_payment_event(tier_idx=None):
    tier = random.choice(TIERS) if tier_idx is None else TIERS[tier_idx % len(TIERS)]
    random_user = f"user_{random.randint(1000, 9999)}@{random.choice(DOMAINS)}"
    transaction_id = f"txn_live_{random.randint(1000000, 9999999)}"
    
    event = {
        "event_id": f"evt_{int(time.time())}_{random.randint(100, 999)}",
        "type": "checkout.session.completed",
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_email": random_user,
        "plan_name": tier["name"],
        "amount_usd": tier["amount"],
        "interval": tier["interval"],
        "transaction_id": transaction_id,
        "status": "PAID_SUCCESSFULLY",
        "currency": "USD"
    }
    return event

if __name__ == "__main__":
    evt = simulate_payment_event()
    print(json.dumps(evt, indent=2))
