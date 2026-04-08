import pandas as pd

print("="*70)
print("COMPLETE DATA SUMMARY")
print("="*70)

# 加载数据
lux_df = pd.read_excel('./political_influencers_Luxembourg_FINAL.xlsx')
fr_df = pd.read_excel('./political_influencers_France.xlsx')
hu_df = pd.read_excel('./political_influencers_Hungary.xlsx')

print("\n1. SAMPLE SIZE")
print("-"*70)
print(f"Luxembourg: {len(lux_df)} videos from {lux_df['channel_name'].nunique()} channels")
print(f"France: {len(fr_df)} videos from {fr_df['channel_name'].nunique()} channels")
print(f"Hungary: {len(hu_df)} videos from {hu_df['channel_name'].nunique()} channels")
print(f"TOTAL: {len(lux_df)+len(fr_df)+len(hu_df)} videos from 60 channels")

print("\n2. DATA FIELDS")
print("-"*70)
print("Available columns:")
for col in lux_df.columns:
    print(f"  - {col}")

print("\n3. LUXEMBOURG CHANNELS (Top 20)")
print("-"*70)
lux_channels = lux_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum'
}).sort_values('view_count', ascending=False)
lux_channels.columns = ['Videos', 'Total Views']
print(lux_channels)

print("\n4. FRANCE CHANNELS (Top 20)")
print("-"*70)
fr_channels = fr_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum'
}).sort_values('view_count', ascending=False)
fr_channels.columns = ['Videos', 'Total Views']
print(fr_channels)

print("\n5. HUNGARY CHANNELS (Top 20)")
print("-"*70)
hu_channels = hu_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum'
}).sort_values('view_count', ascending=False)
hu_channels.columns = ['Videos', 'Total Views']
print(hu_channels)

print("\n6. TIME RANGE")
print("-"*70)
print(f"Luxembourg: {lux_df['published_date'].min()} to {lux_df['published_date'].max()}")
print(f"France: {fr_df['published_date'].min()} to {fr_df['published_date'].max()}")
print(f"Hungary: {hu_df['published_date'].min()} to {hu_df['published_date'].max()}")

print("\n7. BASIC STATISTICS")
print("-"*70)
stats_summary = pd.DataFrame({
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Mean Views': [lux_df['view_count'].mean(), fr_df['view_count'].mean(), hu_df['view_count'].mean()],
    'Median Views': [lux_df['view_count'].median(), fr_df['view_count'].median(), hu_df['view_count'].median()],
    'Mean Likes': [lux_df['like_count'].mean(), fr_df['like_count'].mean(), hu_df['like_count'].mean()],
    'Mean Comments': [lux_df['comment_count'].mean(), fr_df['comment_count'].mean(), hu_df['comment_count'].mean()]
})
print(stats_summary.round(0))

print("\n8. DATA FILES AVAILABLE")
print("-"*70)
import os
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
print(f"Total Excel files: {len(excel_files)}")
for f in sorted(excel_files):
    size = os.path.getsize(f) / 1024
    print(f"  {f} ({size:.1f} KB)")

print("\n" + "="*70)