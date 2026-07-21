def calculate_stalled_timeline(target_amount, history, current_month, window_size=3):
    cumulative_savings = sum(history)
    remaining_balance = max(0, target_amount - cumulative_savings)

    # Extract recent history window
    recent_history = history[-window_size:] if len(history) >= window_size else history

    # Calculate velocity
    # if not recent_history or sum(recent_history) == 0:
    #     velocity = 0
    # else:
    velocity = sum(recent_history) / len(recent_history)

    # CRITICAL: Handle the divide-by-zero flaw safely
    if velocity == 0:
        months_remaining = "Stalled (∞)"
    else:
        months_remaining = round(remaining_balance / velocity, 1)

    return {
        "month": current_month,
        "actual_deposit": history[-1] if history else 0,
        "remaining_balance": remaining_balance,
        "rolling_velocity": round(velocity, 2),
        "dynamic_months_remaining": months_remaining,
    }


# --- SIMULATION (All deposits are Rs. 0) ---
TARGET = 2400000
WINDOW = 3
zero_history = [12000, 0, 3, 100]

print(
    f"{'Month':<6} | {'Deposit':<9} | {'Remaining Bal':<14} | {'Velocity':<10} | {'Months Left':<12}"
)
print("-" * 60)

current_history = []
for index, deposit in enumerate(zero_history, start=1):
    current_history.append(deposit)
    result = calculate_stalled_timeline(TARGET, current_history, index, WINDOW)

    print(
        f"M{result['month']:<5} | Rs.{result['actual_deposit']:<6} | Rs.{result['remaining_balance']:<10} | Rs.{result['rolling_velocity']:<7} | {result['dynamic_months_remaining']:<12}"
    )
