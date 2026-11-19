# DAX Measures (PayFlow dashboard)

Model: `users[user_id]` 1 -> * `transactions[user_id]`; `DimDate[Date]` 1 -> * `transactions[txn_date]`.

```dax
DimDate = ADDCOLUMNS(CALENDAR(DATE(2025,1,1),DATE(2025,12,31)),
  "Month No",MONTH([Date]),"Month",FORMAT([Date],"MMM"),
  "Day Type",IF(WEEKDAY([Date],2)>=6,"Weekend","Weekday"))

-- in Power Query add column txn_date = DateTime.Date([txn_datetime])

Total Transactions = COUNTROWS(transactions)
Successful Txns    = CALCULATE([Total Transactions], transactions[status]="Successful")
Total Value        = SUM(transactions[amount])
Successful Value   = CALCULATE([Total Value], transactions[status]="Successful")
Unique Users       = DISTINCTCOUNT(transactions[user_id])

-- Bug-proof: denominator ignores Status slicer, so rate never exceeds 100%
Success Rate % =
VAR _ok  = CALCULATE([Total Transactions], transactions[status]="Successful")
VAR _all = CALCULATE([Total Transactions], REMOVEFILTERS(transactions[status]))
RETURN DIVIDE(_ok,_all)

Failure Rate % = DIVIDE(CALCULATE([Total Transactions],transactions[status]="Failed"),
                        CALCULATE([Total Transactions],REMOVEFILTERS(transactions[status])))
Avg Ticket Size = DIVIDE([Total Value],[Total Transactions])
Fee Revenue = SUM(transactions[fee])
Weekend Share % = DIVIDE(CALCULATE([Total Transactions],DimDate[Day Type]="Weekend"),CALCULATE([Total Transactions],REMOVEFILTERS(DimDate[Day Type])))

-- Top 5 users by value: use Top N filter on visual (Top 5 by [Total Value])

-- Dynamic insight text (changes with slicers)
Insight Text =
VAR t = TOPN(1,SUMMARIZE(DimDate,DimDate[Day Type],"v",[Total Transactions]),[v],DESC)
VAR top = MAXX(t,DimDate[Day Type])
RETURN "On " & top & "s, transactions are highest ("& FORMAT(MAXX(t,[v]),"#,0") &")"
```
