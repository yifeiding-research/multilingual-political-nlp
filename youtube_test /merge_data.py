import pandas as pd

df1 = pd.read_excel('complete_dataset_with_analysis.xlsx')
df2 = pd.read_excel('complete_dataset_with_sentiment.xlsx')

merged = df1.merge(df2[['video_url', 'sentiment']], on='video_url', how='left')

merged.to_excel('complete_dataset_MERGED.xlsx', index=False)
print("✓ Merged dataset saved")
print(f"Columns: {merged.columns.tolist()}")