import pandas as pd

data = [
    ["Q1 (Low)", "1-682", 412, "0.0246 (0.061)", 0.0000, 0.443, "<.001"],
    ["Q2", "683-2660", 411, "0.0288 (0.038)", 0.0173, 0.246, "<.001"],
    ["Q3", "2661-9964", 411, "0.0403 (0.042)", 0.0320, 0.173, "<.001"],
    ["Q4 (High)", "9965-2664193", 411, "0.0416 (0.035)", 0.0330, -0.199, "<.001"]
]

columns = [
    "Quartile",
    "View Range",
    "N",
    "Mean Engagement (SD)",
    "Median Engagement",
    "Within-Quartile Spearman r_s",
    "p-value"
]

df = pd.DataFrame(data, columns=columns)

print(df)  # 👈 关键：先确认不是空的
df.to_csv("note3.csv", index=False)

