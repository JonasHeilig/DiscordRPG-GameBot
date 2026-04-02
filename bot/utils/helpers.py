import random
import secrets
from config import ORE_TYPES


def calculate_ore_rewards(mining_time_minutes, probabilities):
    base_amount = mining_time_minutes // 5
    if base_amount < 1:
        base_amount = 1

    rewards = {}
    total_probability = sum(probabilities.values())

    num_rolls = max(1, mining_time_minutes // 10)

    for _ in range(num_rolls):
        random_value = random.uniform(0, total_probability)
        current_prob = 0

        for ore_type in ["coal", "iron", "gold", "copper", "diamond", "emerald"]:
            current_prob += probabilities[ore_type]
            if random_value <= current_prob:
                if ore_type not in rewards:
                    rewards[ore_type] = 0
                rewards[ore_type] += base_amount
                break

    return rewards


def generate_token():
    return secrets.token_urlsafe(32)


def validate_mining_time(time_minutes):
    try:
        time_int = int(time_minutes)
        if 1 <= time_int <= 480:
            return time_int
        return None
    except (ValueError, TypeError):
        return None
