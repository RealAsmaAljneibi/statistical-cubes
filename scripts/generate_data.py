"""
Synthetic Employee Register generator.

Produces 50,000 rows of synthetic employee records that mimic the schema
of SCAD's Employee Statistical Register. All values are fully synthetic.
No real persons, employers, or identifiers are referenced.

Run:
    python scripts/generate_data.py

Output:
    data/employee_register_synthetic.csv
"""

import os
import uuid
import numpy as np
import pandas as pd

SEED = 42
N_ROWS = 50_000
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "employee_register_synthetic.csv",
)


def generate():
    rng = np.random.default_rng(SEED)
    np.random.seed(SEED)

    # Reference dates: monthly snapshots 2024-01 to 2024-12
    months = pd.date_range("2024-01-01", "2024-12-01", freq="MS").strftime("%Y-%m-%d").tolist()
    reference_date = rng.choice(months, size=N_ROWS)

    # Employee IDs: synthetic UUIDs (not linked to anything)
    # Build 128-bit ints from two 64-bit halves for reproducibility under seed.
    hi = rng.integers(0, 2**63 - 1, size=N_ROWS, dtype=np.int64).astype(object)
    lo = rng.integers(0, 2**63 - 1, size=N_ROWS, dtype=np.int64).astype(object)
    employee_id = [str(uuid.UUID(int=(int(h) << 64) | int(l))) for h, l in zip(hi, lo)]

    # Age: working-age skew, peak around 30-40
    age = np.clip(rng.normal(35, 10, N_ROWS).round(), 18, 70).astype(int)

    # Gender: ~70 percent Male, 30 percent Female (reflects UAE workforce)
    gender = rng.choice(["Male", "Female"], size=N_ROWS, p=[0.70, 0.30])

    # Nationality: ~30 countries with realistic weights
    nationalities = [
        "United Arab Emirates", "India", "Pakistan", "Philippines", "Egypt",
        "Bangladesh", "Sri Lanka", "Nepal", "Jordan", "Syria",
        "Lebanon", "Sudan", "Yemen", "Morocco", "Tunisia",
        "United Kingdom", "United States", "Canada", "Australia", "France",
        "Germany", "Italy", "Russia", "China", "Indonesia",
        "Iran", "Iraq", "Saudi Arabia", "Oman", "Kuwait",
    ]
    nat_weights = np.array([
        0.15, 0.25, 0.10, 0.08, 0.06,
        0.05, 0.03, 0.025, 0.025, 0.02,
        0.02, 0.015, 0.015, 0.01, 0.01,
        0.012, 0.010, 0.008, 0.006, 0.005,
        0.005, 0.004, 0.004, 0.015, 0.012,
        0.006, 0.005, 0.012, 0.008, 0.006,
    ])
    nat_weights = nat_weights / nat_weights.sum()
    nationality = rng.choice(nationalities, size=N_ROWS, p=nat_weights)

    # Marital status
    marital_status = rng.choice(
        ["Single", "Married", "Divorced", "Widowed"],
        size=N_ROWS,
        p=[0.38, 0.55, 0.05, 0.02],
    )

    # Education
    education_level = rng.choice(
        ["No Formal", "Primary", "Secondary", "Diploma", "Bachelor", "Master", "Doctorate"],
        size=N_ROWS,
        p=[0.03, 0.08, 0.22, 0.18, 0.35, 0.12, 0.02],
    )

    # Specialization
    specialization = rng.choice(
        ["Engineering", "Business", "Health", "IT", "Education", "Arts", "Science", "Law", "Other"],
        size=N_ROWS,
        p=[0.18, 0.22, 0.10, 0.12, 0.08, 0.06, 0.08, 0.05, 0.11],
    )

    # ISCO-08 style 4-digit occupation codes (synthetic selection of ~30)
    occupation_codes = [
        "1120", "1211", "1213", "1219", "2141", "2142", "2151", "2211", "2310", "2320",
        "2330", "2411", "2421", "2511", "2512", "2611", "3112", "3115", "3211", "3221",
        "3322", "3412", "4110", "4222", "5120", "5223", "5414", "7115", "8322", "9112",
    ]
    occupation_unit_group = rng.choice(occupation_codes, size=N_ROWS)

    # ISIC-style activity classes (~20)
    isic_codes = [
        "0111", "1010", "2410", "2511", "3510", "4110", "4520", "4711", "4910", "5510",
        "5610", "6201", "6411", "6810", "7110", "8411", "8510", "8610", "9411", "9700",
    ]
    activity_class = rng.choice(isic_codes, size=N_ROWS)

    # Employment status
    employment_status = rng.choice(
        ["Employer", "Self-employed", "Paid employee", "Family worker"],
        size=N_ROWS,
        p=[0.04, 0.06, 0.88, 0.02],
    )

    # Contract type
    contract_type = rng.choice(
        ["Permanent", "Temporary", "Part-time"],
        size=N_ROWS,
        p=[0.72, 0.20, 0.08],
    )

    # Employer sector
    employer_sector = rng.choice(
        ["Government", "Semi-government", "Private", "Free Zone"],
        size=N_ROWS,
        p=[0.18, 0.12, 0.58, 0.12],
    )

    # Monthly salary: right-skewed lognormal, median around 12,000 AED
    raw_salary = rng.lognormal(mean=np.log(12000), sigma=0.75, size=N_ROWS)
    monthly_salary = np.clip(raw_salary, 3000, 150000).round(0).astype(int)

    # Work emirate
    emirates = ["Abu Dhabi", "Dubai", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
    em_weights = np.array([0.60, 0.20, 0.10, 0.04, 0.03, 0.02, 0.01])
    work_emirate = rng.choice(emirates, size=N_ROWS, p=em_weights)

    # Work region within emirate (plausible synthetic names)
    region_map = {
        "Abu Dhabi": ["Abu Dhabi City", "Al Ain", "Al Dhafra"],
        "Dubai": ["Bur Dubai", "Deira", "Jebel Ali"],
        "Sharjah": ["Sharjah City", "Khor Fakkan", "Kalba"],
        "Ajman": ["Ajman City", "Masfout"],
        "Ras Al Khaimah": ["RAK City", "Al Rams"],
        "Fujairah": ["Fujairah City", "Dibba"],
        "Umm Al Quwain": ["UAQ City"],
    }
    work_region = np.array([rng.choice(region_map[e]) for e in work_emirate])

    # Residence emirate: correlated with work emirate but not identical
    def residence_from_work(work):
        # 80 percent live in same emirate, 20 percent elsewhere
        if rng.random() < 0.80:
            return work
        return rng.choice(emirates, p=em_weights)

    residence_emirate = np.array([residence_from_work(w) for w in work_emirate])

    is_final = np.ones(N_ROWS, dtype=int)

    df = pd.DataFrame({
        "employee_id": employee_id,
        "reference_date": reference_date,
        "age": age,
        "gender": gender,
        "nationality": nationality,
        "marital_status": marital_status,
        "education_level": education_level,
        "specialization": specialization,
        "occupation_unit_group": occupation_unit_group,
        "activity_class": activity_class,
        "employment_status": employment_status,
        "contract_type": contract_type,
        "employer_sector": employer_sector,
        "monthly_salary": monthly_salary,
        "work_emirate": work_emirate,
        "work_region": work_region,
        "residence_emirate": residence_emirate,
        "is_final": is_final,
    })

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} rows to {OUT_PATH}")
    print(f"File size: {os.path.getsize(OUT_PATH) / 1024:.1f} KB")
    return df


if __name__ == "__main__":
    generate()
