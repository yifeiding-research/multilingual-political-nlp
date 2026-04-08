import pandas as pd

fr_df = pd.read_excel('./political_influencers_France.xlsx')
hu_df = pd.read_excel('./political_influencers_Hungary.xlsx')

print("="*70)
print("FRANCE - TOP 10 CHANNELS")
print("="*70)
fr_summary = fr_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum'
}).sort_values('view_count', ascending=False).head(10)
print(fr_summary)

print("\n" + "="*70)
print("HUNGARY - TOP 10 CHANNELS")
print("="*70)
hu_summary = hu_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum'
}).sort_values('view_count', ascending=False).head(10)
print(hu_summary)

print("\n" + "="*70)
print("DATA QUALITY CHECK")
print("="*70)
print(f"France: {len(fr_df)} videos, {fr_df['channel_name'].nunique()} channels")
print(f"Hungary: {len(hu_df)} videos, {hu_df['channel_name'].nunique()} channels")

print("\nAre these legitimate political influencers? (y/n)")