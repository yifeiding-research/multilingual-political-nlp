import pandas as pd
from langdetect import detect_langs
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

lux_df = pd.read_excel('./political_influencers_Luxembourg_NEW.xlsx')
fr_df = pd.read_excel('./political_influencers_France.xlsx')
hu_df = pd.read_excel('./political_influencers_Hungary.xlsx')

all_df = pd.concat([lux_df, fr_df, hu_df])

def detect_languages(text):
    try:
        langs = detect_langs(str(text))
        return {
            'primary_language': langs[0].lang if langs else None,
            'language_confidence': langs[0].prob if langs else 0,
            'all_languages': [l.lang for l in langs if l.prob > 0.2],
            'num_languages': len([l for l in langs if l.prob > 0.2]),
            'is_multilingual': len([l for l in langs if l.prob > 0.2]) > 1
        }
    except:
        return {
            'primary_language': None,
            'language_confidence': 0,
            'all_languages': [],
            'num_languages': 0,
            'is_multilingual': False
        }

print("Analyzing languages...")
all_df['language_analysis'] = all_df['video_title'].apply(detect_languages)
all_df['primary_language'] = all_df['language_analysis'].apply(lambda x: x['primary_language'])
all_df['is_multilingual'] = all_df['language_analysis'].apply(lambda x: x['is_multilingual'])
all_df['num_languages'] = all_df['language_analysis'].apply(lambda x: x['num_languages'])

all_df['engagement_rate'] = (all_df['like_count'] + all_df['comment_count']) / all_df['view_count'].replace(0, 1)

print("\n" + "="*70)
print("DATASET SUMMARY")
print("="*70)
print(f"Total videos: {len(all_df)}")
print(f"Luxembourg: {len(lux_df)} videos, {lux_df['channel_name'].nunique()} channels")
print(f"France: {len(fr_df)} videos, {fr_df['channel_name'].nunique()} channels")
print(f"Hungary: {len(hu_df)} videos, {hu_df['channel_name'].nunique()} channels")

print("\n" + "="*70)
print("H1: LANGUAGE STRATEGY HYPOTHESIS")
print("="*70)

lux_multi = all_df[all_df['country']=='Luxembourg']['is_multilingual'].mean()
fr_multi = all_df[all_df['country']=='France']['is_multilingual'].mean()
hu_multi = all_df[all_df['country']=='Hungary']['is_multilingual'].mean()

print(f"\nMultilingual content rate:")
print(f"Luxembourg: {lux_multi:.2%}")
print(f"France: {fr_multi:.2%}")
print(f"Hungary: {hu_multi:.2%}")

print(f"\nLanguage distribution:")
for country in ['Luxembourg', 'France', 'Hungary']:
    country_df = all_df[all_df['country']==country]
    lang_dist = country_df['primary_language'].value_counts().head(5)
    print(f"\n{country}:")
    for lang, count in lang_dist.items():
        pct = count / len(country_df) * 100
        print(f"  {lang}: {count} ({pct:.1f}%)")

chi2, p_value = stats.chi2_contingency([
    [sum(all_df[all_df['country']=='Luxembourg']['is_multilingual']), 
     sum(~all_df[all_df['country']=='Luxembourg']['is_multilingual'])],
    [sum(all_df[all_df['country']=='France']['is_multilingual']), 
     sum(~all_df[all_df['country']=='France']['is_multilingual'])]
])[:2]

print(f"\nStatistical test (Lux vs France):")
print(f"Chi-square p-value: {p_value:.6f}")
if p_value < 0.05:
    print("✓ SIGNIFICANT: Luxembourg has different multilingual strategy")
else:
    print("✗ Not significant")

print("\n" + "="*70)
print("H3: SMALL STATE ENGAGEMENT HYPOTHESIS")
print("="*70)

lux_eng = all_df[all_df['country']=='Luxembourg']['engagement_rate'].mean()
fr_eng = all_df[all_df['country']=='France']['engagement_rate'].mean()
hu_eng = all_df[all_df['country']=='Hungary']['engagement_rate'].mean()

lux_views = all_df[all_df['country']=='Luxembourg']['view_count'].mean()
fr_views = all_df[all_df['country']=='France']['view_count'].mean()
hu_views = all_df[all_df['country']=='Hungary']['view_count'].mean()

print(f"\nEngagement rate (likes+comments/views):")
print(f"Luxembourg: {lux_eng:.4f} ({lux_eng*100:.2f}%)")
print(f"France: {fr_eng:.4f} ({fr_eng*100:.2f}%)")
print(f"Hungary: {hu_eng:.4f} ({hu_eng*100:.2f}%)")

print(f"\nAverage views per video:")
print(f"Luxembourg: {lux_views:,.0f}")
print(f"France: {fr_views:,.0f}")
print(f"Hungary: {hu_views:,.0f}")

t_stat, p_value_eng = stats.ttest_ind(
    all_df[all_df['country']=='Luxembourg']['engagement_rate'].dropna(),
    all_df[all_df['country']=='France']['engagement_rate'].dropna()
)

t_stat2, p_value_views = stats.ttest_ind(
    all_df[all_df['country']=='Luxembourg']['view_count'].dropna(),
    all_df[all_df['country']=='France']['view_count'].dropna()
)

print(f"\nStatistical tests (Lux vs France):")
print(f"Engagement rate t-test p-value: {p_value_eng:.6f}")
if p_value_eng < 0.05:
    if lux_eng > fr_eng:
        print("✓ SIGNIFICANT: Luxembourg has HIGHER engagement")
    else:
        print("✓ SIGNIFICANT: Luxembourg has LOWER engagement")
else:
    print("✗ Not significant")

print(f"\nViews t-test p-value: {p_value_views:.6f}")
if p_value_views < 0.05:
    if lux_views < fr_views:
        print("✓ SIGNIFICANT: Luxembourg has LOWER reach (smaller market)")
    else:
        print("✓ SIGNIFICANT: Luxembourg has HIGHER reach")
else:
    print("✗ Not significant")

channel_summary = all_df.groupby(['country', 'channel_name']).agg({
    'video_title': 'count',
    'view_count': ['sum', 'mean'],
    'like_count': ['sum', 'mean'],
    'comment_count': ['sum', 'mean'],
    'engagement_rate': 'mean',
    'is_multilingual': 'mean'
}).reset_index()

channel_summary.columns = ['country', 'channel', 'total_videos', 'total_views', 'avg_views', 
                           'total_likes', 'avg_likes', 'total_comments', 'avg_comments', 
                           'avg_engagement', 'multilingual_rate']

print("\n" + "="*70)
print("TOP 5 INFLUENCERS PER COUNTRY (by total views)")
print("="*70)

for country in ['Luxembourg', 'France', 'Hungary']:
    print(f"\n{country}:")
    top5 = channel_summary[channel_summary['country']==country].nlargest(5, 'total_views')
    for idx, row in top5.iterrows():
        print(f"  {row['channel']}")
        print(f"    Views: {row['total_views']:,.0f} | Videos: {row['total_videos']:.0f} | Engagement: {row['avg_engagement']:.4f}")

plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 3, figsize=(18, 12))

multi_data = [lux_multi*100, fr_multi*100, hu_multi*100]
axes[0, 0].bar(['Luxembourg', 'France', 'Hungary'], multi_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 0].set_ylabel('Percentage (%)', fontsize=12)
axes[0, 0].set_title('H1: Multilingual Content Rate', fontsize=14, fontweight='bold')
axes[0, 0].set_ylim(0, max(multi_data)*1.3)
for i, v in enumerate(multi_data):
    axes[0, 0].text(i, v+1, f'{v:.1f}%', ha='center', fontsize=11)

eng_data = [lux_eng*100, fr_eng*100, hu_eng*100]
axes[0, 1].bar(['Luxembourg', 'France', 'Hungary'], eng_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 1].set_ylabel('Engagement Rate (%)', fontsize=12)
axes[0, 1].set_title('H3: Engagement Rate', fontsize=14, fontweight='bold')
for i, v in enumerate(eng_data):
    axes[0, 1].text(i, v*0.05, f'{v:.2f}%', ha='center', fontsize=11)

view_data = [lux_views/1000, fr_views/1000, hu_views/1000]
axes[0, 2].bar(['Luxembourg', 'France', 'Hungary'], view_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 2].set_ylabel('Average Views (thousands)', fontsize=12)
axes[0, 2].set_title('H3: Average Video Reach', fontsize=14, fontweight='bold')
for i, v in enumerate(view_data):
    axes[0, 2].text(i, v*0.05, f'{v:.1f}K', ha='center', fontsize=11)

for country, color in zip(['Luxembourg', 'France', 'Hungary'], ['#3498db', '#e74c3c', '#2ecc71']):
    data = all_df[all_df['country']==country]['engagement_rate'].dropna()
    axes[1, 0].hist(data, bins=50, alpha=0.6, label=country, color=color, range=(0, 0.15))
axes[1, 0].set_xlabel('Engagement Rate', fontsize=12)
axes[1, 0].set_ylabel('Frequency', fontsize=12)
axes[1, 0].set_title('Engagement Distribution', fontsize=14, fontweight='bold')
axes[1, 0].legend(fontsize=10)

lang_data = {}
for country in ['Luxembourg', 'France', 'Hungary']:
    country_df = all_df[all_df['country']==country]
    lang_counts = country_df['primary_language'].value_counts().head(5)
    lang_data[country] = lang_counts

lux_langs = lang_data['Luxembourg']
axes[1, 1].pie(lux_langs.values, labels=lux_langs.index, autopct='%1.1f%%', startangle=90)
axes[1, 1].set_title('Luxembourg Language Distribution', fontsize=14, fontweight='bold')

videos_data = [len(lux_df), len(fr_df), len(hu_df)]
axes[1, 2].bar(['Luxembourg', 'France', 'Hungary'], videos_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[1, 2].set_ylabel('Number of Videos', fontsize=12)
axes[1, 2].set_title('Dataset Size', fontsize=14, fontweight='bold')
for i, v in enumerate(videos_data):
    axes[1, 2].text(i, v*0.02, f'{v:,}', ha='center', fontsize=11)

plt.tight_layout()
plt.savefig('complete_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved: complete_analysis.png")

all_df.to_excel('complete_dataset_with_analysis.xlsx', index=False)
channel_summary.to_excel('channel_summary_final.xlsx', index=False)

summary_stats = pd.DataFrame({
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Videos': [len(lux_df), len(fr_df), len(hu_df)],
    'Channels': [lux_df['channel_name'].nunique(), fr_df['channel_name'].nunique(), hu_df['channel_name'].nunique()],
    'Multilingual %': [lux_multi*100, fr_multi*100, hu_multi*100],
    'Avg Engagement %': [lux_eng*100, fr_eng*100, hu_eng*100],
    'Avg Views': [lux_views, fr_views, hu_views]
})
summary_stats.to_excel('summary_final.xlsx', index=False)

print("\n" + "="*70)
print("FILES SAVED")
print("="*70)
print("1. complete_analysis.png - 6 visualizations")
print("2. complete_dataset_with_analysis.xlsx - All videos with language analysis")
print("3. channel_summary_final.xlsx - 60 channels summary")
print("4. summary_final.xlsx - Country comparison table")
print("="*70)
