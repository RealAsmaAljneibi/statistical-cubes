"""
Abu Dhabi Labour Force Register — Quarterly Synthetic Data Generator
2020 Q1 to 2026 Q2  ·  ~500,000 employee records  ·  26 quarterly snapshots

Geographic scope: Abu Dhabi Emirate only
  - Abu Dhabi Region  (72 % of workforce)
  - Al Ain Region     (22 %)
  - Al Dhafra Region  ( 6 % — mainly oil, gas, agriculture)

Trends encoded:
  - Workforce grows from 16 000 to 23 000 per quarter (→ ~500 K total)
  - Female participation rises: 27 % (2020 Q1) → 33 % (2026 Q2)
  - Tertiary education share rises: 46 % → 54 %
  - Salaries grow ~3 % / year
  - COVID dip Q2–Q3 2020: private sector down 12 %
  - Al Dhafra oil-sector rebound 2021-2022 (oil price recovery)

Run:
    python scripts/generate_quarterly_data.py

Output:
    data/employee_register_quarterly.csv
"""

import os
import uuid
import numpy as np
import pandas as pd

SEED   = 99
TARGET = 500_000
OUT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "employee_register_quarterly.csv",
)

QUARTERS = pd.date_range("2020-01-01", "2026-04-01", freq="QS")  # 26 quarters


# ── Geographic structure (Abu Dhabi Emirate) ──────────────────────────────────
REGIONS = ["Abu Dhabi Region", "Al Ain Region", "Al Dhafra Region"]
REGION_W = np.array([0.72, 0.22, 0.06])

DISTRICT_MAP = {
    "Abu Dhabi Region": [
        "Abu Dhabi City", "Khalifa City", "Mohammed Bin Zayed City",
        "Zayed City", "Musaffah", "Al Reem Island", "Yas Island",
    ],
    "Al Ain Region": [
        "Al Ain City", "Al Hili", "Al Muwaiji",
        "Al Yahar", "Al Qattara", "Hili Industrial",
    ],
    "Al Dhafra Region": [
        "Madinat Zayed", "Ruwais", "Liwa", "Al Mirfa",
    ],
}

# ── Nationality pool ──────────────────────────────────────────────────────────
NATIONALITIES = [
    "United Arab Emirates", "India", "Pakistan", "Philippines", "Egypt",
    "Bangladesh", "Sri Lanka", "Nepal", "Jordan", "Syria",
    "Lebanon", "Sudan", "Yemen", "Morocco", "Tunisia",
    "United Kingdom", "United States", "Canada", "Australia", "France",
    "Germany", "Italy", "Russia", "China", "Indonesia",
    "Iran", "Iraq", "Saudi Arabia", "Oman", "Kuwait",
    "Ethiopia", "Ghana", "Kenya", "Nigeria", "South Africa",
]
NAT_W = np.array([
    0.14, 0.24, 0.10, 0.07, 0.07,
    0.05, 0.03, 0.03, 0.02, 0.02,
    0.02, 0.015, 0.015, 0.01, 0.01,
    0.012, 0.010, 0.007, 0.006, 0.005,
    0.005, 0.004, 0.004, 0.014, 0.011,
    0.006, 0.005, 0.011, 0.007, 0.005,
    0.006, 0.005, 0.004, 0.006, 0.004,
])
NAT_W /= NAT_W.sum()

# ── Occupation (ISCO-08 4-digit) ──────────────────────────────────────────────
OCC_POOL = [
    ("1120", 0.015), ("1211", 0.012), ("1219", 0.012), ("1321", 0.010),
    ("2141", 0.035), ("2142", 0.030), ("2151", 0.020), ("2166", 0.012),
    ("2211", 0.025), ("2310", 0.020), ("2320", 0.018), ("2330", 0.015),
    ("2411", 0.030), ("2421", 0.018), ("2422", 0.015), ("2511", 0.040),
    ("2512", 0.035), ("2611", 0.025), ("3112", 0.020), ("3115", 0.018),
    ("3211", 0.015), ("3221", 0.012), ("3322", 0.020), ("3412", 0.015),
    ("4110", 0.040), ("4222", 0.025), ("5120", 0.030), ("5223", 0.025),
    ("5414", 0.025), ("6111", 0.015), ("7111", 0.012), ("7115", 0.015),
    ("8322", 0.025), ("9112", 0.035), ("9333", 0.030),
]
OCC_CODES, OCC_W_RAW = zip(*OCC_POOL)
OCC_W = np.array(OCC_W_RAW) / sum(OCC_W_RAW)

# ── Economic activity (ISIC) ──────────────────────────────────────────────────
ISIC_POOL = [
    ("0111", 0.02), ("0610", 0.03), ("1010", 0.01), ("2410", 0.02),
    ("2511", 0.02), ("3510", 0.03), ("4110", 0.06), ("4520", 0.04),
    ("4711", 0.04), ("4910", 0.02), ("5510", 0.02), ("5610", 0.04),
    ("6201", 0.05), ("6411", 0.04), ("6810", 0.05), ("7110", 0.04),
    ("7490", 0.03), ("8411", 0.06), ("8510", 0.05), ("8610", 0.04),
    ("8710", 0.02), ("9000", 0.02), ("9411", 0.02), ("9700", 0.02),
]
ISIC_CODES, ISIC_W_RAW = zip(*ISIC_POOL)
ISIC_W = np.array(ISIC_W_RAW) / sum(ISIC_W_RAW)

# ── Education specializations ─────────────────────────────────────────────────
SPECS = [
    "Engineering & Technology", "Business & Management", "Health & Medicine",
    "Information Technology", "Education & Teaching", "Law & Legal Studies",
    "Sciences & Mathematics", "Architecture & Urban Planning",
    "Arts & Humanities", "Agriculture & Environment", "Other",
]
SPEC_W = np.array([0.18, 0.20, 0.10, 0.13, 0.08, 0.05, 0.08, 0.06, 0.05, 0.04, 0.03])
SPEC_W /= SPEC_W.sum()


def lerp(t, a, b):
    return a + t * (b - a)


def generate_quarter(rng, qdate, t_pos, q_idx):
    """Generate one quarterly register snapshot for Abu Dhabi Emirate."""
    n_base = int(lerp(t_pos, 16_000, 23_000))

    # COVID dip: Q2–Q3 2020 (indices 1, 2)
    is_covid = q_idx in (1, 2)
    n = int(n_base * (0.88 if is_covid else 1.0))

    # Sector weights — ADRD Employer Sector codes 01/02/04/05/06/08
    # Oil-price recovery 2021-2022 boosts Public Enterprises (ADNOC, Mubadala)
    is_oil_recovery = 9 <= q_idx <= 13   # 2022 Q2 – 2023 Q2
    fed_gov_share    = lerp(t_pos, 0.05, 0.06)
    local_gov_share  = lerp(t_pos, 0.17, 0.20)
    pub_ent_share    = lerp(t_pos, 0.17, 0.21) * (1.12 if is_oil_recovery else 1.0)
    priv_ent_share   = lerp(t_pos, 0.51, 0.44) * (0.88 if is_covid else 1.0)
    foreign_ent_share = lerp(t_pos, 0.08, 0.09)
    household_share  = lerp(t_pos, 0.02, 0.02)
    sec_p = np.array([fed_gov_share, local_gov_share, pub_ent_share,
                      priv_ent_share, foreign_ent_share, household_share])
    sec_p = np.clip(sec_p, 0.005, 1.0)
    sec_p /= sec_p.sum()

    # Female participation trend
    female_p = lerp(t_pos, 0.27, 0.33)

    # Education shift toward tertiary
    edu_shift = lerp(t_pos, 0, 0.08)
    edu_p = np.array([
        0.03,
        0.07,
        0.20,
        0.18,
        max(0.30 - edu_shift / 2, 0.22),
        max(0.15 + edu_shift / 3, 0.15),
        max(0.07 + edu_shift / 6, 0.07),
    ])
    edu_p /= edu_p.sum()

    # Salary growth
    salary_mult = 1.03 ** (q_idx / 4)

    # Region distribution: Al Dhafra grows during oil recovery
    region_w = REGION_W.copy()
    if is_oil_recovery:
        region_w[2] *= 1.4   # Al Dhafra grows
        region_w /= region_w.sum()

    # Generate fields
    age      = np.clip(rng.normal(34, 10, n).round(), 18, 70).astype(int)
    gender   = rng.choice(["Male", "Female"], size=n, p=[1 - female_p, female_p])
    nat      = rng.choice(NATIONALITIES, size=n, p=NAT_W)
    marital  = rng.choice(
        ["Never married", "Married", "Divorced", "Widowed"],
        size=n, p=[0.36, 0.57, 0.05, 0.02],
    )
    edu = rng.choice(
        ["No Formal", "Primary", "Secondary", "Diploma", "Bachelor", "Master", "Doctorate"],
        size=n, p=edu_p,
    )
    spec = rng.choice(SPECS, size=n, p=SPEC_W)
    occ  = rng.choice(OCC_CODES, size=n, p=OCC_W)
    act  = rng.choice(ISIC_CODES, size=n, p=ISIC_W)
    emp_status = rng.choice(
        ["Employer", "Self-employed", "Paid employee", "Family worker"],
        size=n, p=[0.04, 0.06, 0.88, 0.02],
    )
    contract = rng.choice(
        ["Permanent", "Temporary", "Part-time"],
        size=n, p=[0.70, 0.22, 0.08],
    )
    # ADRD Employer Sector labels (codes 01, 02, 04, 05, 06, 08)
    sector = rng.choice(
        ["Federal Government", "Local Government", "Public Enterprises",
         "Private Enterprises", "Foreign Enterprises", "Household"],
        size=n, p=sec_p,
    )

    # Salary: correlated with sector and education
    base_salary = np.where(
        sector == "Public Enterprises", 28000,   # ADNOC, Mubadala, TAQA
        np.where(sector == "Local Government", 22000,
        np.where(sector == "Federal Government", 20000,
        np.where(sector == "Foreign Enterprises", 14000,
        np.where(sector == "Household", 4000, 11000))))
    )
    edu_bonus = np.select(
        [edu == "Doctorate", edu == "Master", edu == "Bachelor",
         edu == "Diploma", edu == "Secondary"],
        [2.2, 1.6, 1.25, 1.05, 0.85], default=0.70,
    )
    raw_salary = rng.lognormal(
        mean=np.log(base_salary * edu_bonus * salary_mult), sigma=0.55, size=n
    )
    salary = np.clip(raw_salary, 3000, 300000).round(0).astype(int)

    # Regions and districts
    work_region = rng.choice(REGIONS, size=n, p=region_w)
    work_district = np.array([
        rng.choice(DISTRICT_MAP[r]) for r in work_region
    ])
    # 85% live in same region, 10% across Abu Dhabi regions, 5% other emirates
    def _res(region, rng=rng):
        p = rng.random()
        if p < 0.83:
            return region
        elif p < 0.95:
            return rng.choice(REGIONS)
        else:
            return rng.choice(["Dubai", "Sharjah"])
    res_region = np.array([_res(r) for r in work_region])

    # UUIDs
    hi = rng.integers(0, 2**63 - 1, size=n, dtype=np.int64).astype(object)
    lo = rng.integers(0, 2**63 - 1, size=n, dtype=np.int64).astype(object)
    emp_ids = [str(uuid.UUID(int=(int(h) << 64) | int(l))) for h, l in zip(hi, lo)]

    q_label = f"Q{(qdate.month - 1) // 3 + 1}"
    return pd.DataFrame({
        "employee_id":       emp_ids,
        "reference_date":    qdate.strftime("%Y-%m-%d"),
        "year":              qdate.year,
        "quarter":           q_label,
        "year_quarter":      f"{qdate.year}-{q_label}",
        "age":               age,
        "gender":            gender,
        "nationality":       nat,
        "marital_status":    marital,
        "education_level":   edu,
        "specialization":    spec,
        "occupation_unit_group": occ,
        "activity_class":    act,
        "employment_status": emp_status,
        "contract_type":     contract,
        "employer_sector":   sector,
        "monthly_salary":    salary,
        "work_emirate":      "Abu Dhabi",
        "work_region":       work_region,
        "work_district":     work_district,
        "residence_region":  res_region,
        "is_final":          1,
    })


def generate():
    rng = np.random.default_rng(SEED)
    frames = []
    n_q = len(QUARTERS)
    for i, qdate in enumerate(QUARTERS):
        t_pos = i / (n_q - 1)
        frame = generate_quarter(rng, qdate, t_pos, i)
        frames.append(frame)
        q_label = f"Q{(qdate.month-1)//3+1}"
        print(f"  {qdate.year}-{q_label}  {len(frame):,} rows")

    result = pd.concat(frames, ignore_index=True)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    result.to_csv(OUT_PATH, index=False)
    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nWrote {len(result):,} rows  ·  {n_q} quarters  →  {OUT_PATH}")
    print(f"File size: {size_mb:.1f} MB")
    return result


if __name__ == "__main__":
    generate()
