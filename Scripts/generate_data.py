"""Synthetic digital-payments dataset (fictional brand: PayFlow). Seeded -> reproducible."""
import os
import numpy as np, pandas as pd
rng = np.random.default_rng(42)

N_USERS, N_TXN = 8000, 150000
first = ["Aarav","Vivaan","Aditya","Arjun","Karthik","Rahul","Rohit","Suresh","Vijay","Manoj","Dinesh","Praveen","Arun","Ganesh","Naveen",
         "Priya","Ananya","Divya","Kavya","Meena","Lakshmi","Sneha","Pooja","Deepa","Anjali","Swathi","Nithya","Revathi","Shruti","Isha"]
last = ["Kumar","Sharma","Reddy","Nair","Iyer","Patel","Singh","Gowda","Rao","Pillai","Das","Mehta","Joshi","Menon","Naidu","Raj","Verma","Shetty"]
states = {"Maharashtra":.14,"Karnataka":.12,"Tamil Nadu":.11,"Uttar Pradesh":.10,"Telangana":.08,"Gujarat":.08,"Delhi":.07,
          "West Bengal":.06,"Kerala":.06,"Rajasthan":.05,"Madhya Pradesh":.04,"Haryana":.04,"Punjab":.03,"Bihar":.02}
cities = {"Maharashtra":["Mumbai","Pune","Nagpur"],"Karnataka":["Bengaluru","Mysuru","Mangaluru"],"Tamil Nadu":["Chennai","Coimbatore","Tiruppur"],
 "Uttar Pradesh":["Lucknow","Noida","Kanpur"],"Telangana":["Hyderabad","Warangal"],"Gujarat":["Ahmedabad","Surat"],"Delhi":["New Delhi"],
 "West Bengal":["Kolkata","Siliguri"],"Kerala":["Kochi","Thiruvananthapuram"],"Rajasthan":["Jaipur","Jodhpur"],"Madhya Pradesh":["Bhopal","Indore"],
 "Haryana":["Gurugram","Faridabad"],"Punjab":["Ludhiana","Amritsar"],"Bihar":["Patna","Gaya"]}

# ---- users
age = np.clip(rng.normal(32,9,N_USERS).round(),18,65).astype(int)
def grp(a): return "Gen Z (18-26)" if a<=26 else "Millennials (27-42)" if a<=42 else "Gen X (43-58)" if a<=58 else "Boomers (59+)"
st = rng.choice(list(states), N_USERS, p=np.array(list(states.values()))/sum(states.values()))
users = pd.DataFrame({
 "user_id":[f"U{100000+i}" for i in range(N_USERS)],
 "user_name":[f"{rng.choice(first)} {rng.choice(last)}" for _ in range(N_USERS)],
 "age":age,"age_group":[grp(a) for a in age],
 "gender":rng.choice(["Male","Female","Other"],N_USERS,p=[.57,.42,.01]),
 "state":st,"city":[rng.choice(cities[s]) for s in st],
 "signup_date":pd.to_datetime("2022-01-01")+pd.to_timedelta(rng.integers(0,1095,N_USERS),unit="D"),
})
users["signup_date"]=users["signup_date"].dt.date

# ---- transactions (calendar 2025) with seasonality + weekday/weekend + heavy-user skew
days = pd.date_range("2025-01-01","2025-12-31")
mw = np.array([.95,.90,.97,.98,1.0,1.0,1.02,1.0,1.03,1.15,1.12,1.08])   # festive bump Oct-Dec
dw = np.where(days.dayofweek<5,1.25,0.75)
w = mw[days.month-1]*dw; w=w/w.sum()
d = rng.choice(days,N_TXN,p=w)
secs = rng.choice(86400,N_TXN,p=np.r_[np.full(6*3600,.4),np.full(4*3600,1.2),np.full(8*3600,1.6),np.full(6*3600,1.5)]/ (np.r_[np.full(6*3600,.4),np.full(4*3600,1.2),np.full(8*3600,1.6),np.full(6*3600,1.5)].sum()))
ts = pd.to_datetime(d)+pd.to_timedelta(secs,unit="s")
uw = rng.pareto(2.0,N_USERS)+1; uw/=uw.sum()
uid = rng.choice(users.user_id,N_TXN,p=uw)

svc = {"Money Transfer":(.28,(6.2,.9)),"Shopping":(.17,(6.8,1.0)),"Bill Payment":(.15,(7.0,.7)),"Mobile Recharge":(.13,(5.6,.6)),
       "Food & Dining":(.10,(5.9,.6)),"Travel":(.07,(7.6,1.0)),"Loans & EMI":(.04,(8.6,.6)),"Insurance":(.03,(8.4,.7)),"Investments":(.03,(8.3,.9))}
s = rng.choice(list(svc),N_TXN,p=np.array([v[0] for v in svc.values()])/sum(v[0] for v in svc.values()))
amt = np.array([rng.lognormal(*svc[x][1]) for x in s]).round(2)
amt = np.clip(amt,10,200000)
pm = rng.choice(["UPI","Debit Card","Credit Card","Wallet","Net Banking"],N_TXN,p=[.68,.12,.10,.06,.04])
# status: failure risk higher for net banking / cards / big amounts / late night
pf = .018+np.where(pm=="Net Banking",.02,0)+np.where(pm=="Credit Card",.008,0)+np.where(amt>50000,.012,0)+np.where(ts.hour<5,.01,0)
r = rng.random(N_TXN)
status = np.where(r<pf,"Failed",np.where(r<pf+.015,"Pending","Successful"))
reasons = rng.choice(["Insufficient Balance","Bank Server Down","Wrong PIN","Network Timeout","Daily Limit Exceeded"],N_TXN,p=[.30,.25,.20,.15,.10])
fee = np.where((status=="Successful")&np.isin(pm,["Credit Card","Debit Card","Net Banking"]),(amt*.009).round(2),0.0)
tx = pd.DataFrame({"txn_id":[f"T{10000000+i}" for i in range(N_TXN)],"user_id":uid,"txn_datetime":ts,"service_type":s,
  "payment_method":pm,"amount":amt,"status":status,"fee":fee,"failure_reason":np.where(status=="Failed",reasons,""),
  "device":rng.choice(["Android","iOS","Web"],N_TXN,p=[.72,.24,.04])}).sort_values("txn_datetime")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"); os.makedirs(out, exist_ok=True)
tx.to_csv(os.path.join(out, "transactions.csv"), index=False); users.to_csv(os.path.join(out, "users.csv"), index=False)
print(tx.shape,users.shape)
