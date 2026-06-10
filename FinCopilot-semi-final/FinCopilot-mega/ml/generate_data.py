"""
Synthetic Student Spending Data Generator
Generates 500 rows of realistic student spending patterns.
"""

import csv
import os
import random
import math


def generate_data(num_rows: int = 500, seed: int = 42) -> list[dict]:
    """Generate synthetic student spending data."""
    random.seed(seed)
    base_spend = 9000  # typical student monthly spend ₹
    rows = []

    for i in range(num_rows):
        month_idx = (i % 12) + 1

        # Exam months: March, April, November
        is_exam = 1 if month_idx in (3, 4, 11) else 0
        # Festival months: October, December, January
        is_festival = 1 if month_idx in (1, 10, 12) else 0

        # Spending with seasonal adjustments
        spend = base_spend
        spend += -800 + _noise(200) if is_exam else 0
        spend += 2500 + _noise(800) if is_festival else 0
        spend += _noise(1200)

        # Previous 3-month average (smoothed)
        prev_base = base_spend + _noise(600)
        avg_prev3 = round(prev_base + (500 if is_festival else 0) + (-300 if is_exam else 0))

        total_spend = max(3000, round(spend))

        rows.append({
            "month_idx": month_idx,
            "is_exam": is_exam,
            "is_festival": is_festival,
            "avg_prev3": avg_prev3,
            "total_spend": total_spend,
        })

    return rows


def _noise(amplitude: float) -> float:
    """Box-Muller normal approximation."""
    u1 = random.random()
    u2 = random.random()
    z = math.sqrt(-2 * math.log(max(u1, 1e-10))) * math.cos(2 * math.pi * u2)
    return round(z * amplitude * 0.5)


def save_csv(rows: list[dict], path: str):
    """Save rows to CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["month_idx", "is_exam", "is_festival", "avg_prev3", "total_spend"])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    csv_path = os.path.join(data_dir, "training_data.csv")
    rows = generate_data(500)
    save_csv(rows, csv_path)
    print(f"[OK] Generated {len(rows)} rows -> {csv_path}")
