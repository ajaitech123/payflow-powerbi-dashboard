# PayFlow – Digital Payments Insights (Power BI)

![PayFlow Dashboard](assets/dashboard_preview.png)

An interactive Power BI dashboard that analyses **150,000 digital payment transactions** from **8,000 users across 14 Indian states** (calendar year 2025).
The brand "PayFlow" and the data are fictional. The dataset is generated with a seeded Python script, so anyone can reproduce it exactly.

## What the dashboard shows
- KPIs: total transactions, total value, unique users, success rate
- Monthly transaction trend
- Age segment contribution
- Service-wise transaction value
- Top 5 users by transaction value
- Weekday vs weekend usage
- Why transactions fail (failure reasons)
- Month and Payment Status slicers, plus a dynamic insight text

## Key findings
| Metric | Result |
|---|---|
| Total value | ₹239.6M (about ₹24 crore) |
| Success / Failed / Pending | 96.5% / 2.0% / 1.5% |
| Weekday share of transactions | ~81% (weekends ~19%) |
| Peak month | October (festive months Oct–Dec are the busiest) |
| Top services by value | Loans & EMI, Shopping, Travel |
| Top failure reasons | Insufficient Balance (29%), Bank Server Down (25%), Wrong PIN (20%) |

## Data model
Star schema: `users` (1) → `transactions` (many) ← `DimDate` (1).

| Table | Key columns |
|---|---|
| `users` | user_id, user_name, age, age_group, gender, state, city, signup_date |
| `transactions` | txn_id, user_id, txn_datetime, service_type, payment_method, amount, status, fee, failure_reason, device |
| `DimDate` | Date, Month No, Month, Day Type (DAX calculated table) |

## DAX highlights
All measures are in [`dax_measures.md`](dax_measures.md). One detail I focused on:
`Success Rate %` removes the Status filter from the denominator (`REMOVEFILTERS`), so it never goes past 100% when the Status slicer is set to Failed. The insight text is also a measure, so it changes with the slicers.

## Tools and skills
Power BI · Power Query · DAX · Data modelling (star schema) · Python (pandas, NumPy) for synthetic data generation

## Repo structure
```
payflow-powerbi-dashboard/
├── PayFlow_Dashboard.pbix
├── README.md
├── dax_measures.md
├── requirements.txt
├── data/        transactions.csv, users.csv
├── scripts/     generate_data.py
├── theme/       PayFlow_Purple_Theme.json
└── assets/      dashboard_preview.png, logo and illustrations
```

## Run it yourself
1. Open `PayFlow_Dashboard.pbix` in Power BI Desktop.
2. To regenerate the data: `pip install -r requirements.txt` then `python scripts/generate_data.py` (output goes to `data/`, seed 42).
3. If Power BI asks for the data source path, Home → Transform data → Data source settings, and point it to the `data/` folder.
4. Optional theme: View → Themes → Browse for themes → `theme/PayFlow_Purple_Theme.json`.

> The data is synthetic and for portfolio purposes only. Illustrations and logo are original.
