import pandas as pd
from langdetect import detect_langs
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

lux_df = pd.read_excel('./political_influencers_Luxembourg_FINAL.xlsx')
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
print("CORRECTED DATASET SUMMARY")
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

print(f"\nEngagement rate:")
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
print(f"Engagement rate p-value: {p_value_eng:.6f}")
if p_value_eng < 0.05:
    if lux_eng > fr_eng:
        print("✓ SIGNIFICANT: Luxembourg has HIGHER engagement")
    else:
        print("✓ SIGNIFICANT: Luxembourg has LOWER engagement") 
else:
    print("✗ Not significant")

print(f"\nViews p-value: {p_value_views:.6f}")
if p_value_views < 0.05:
    if lux_views < fr_views:
        print("✓ SIGNIFICANT: Luxembourg has LOWER reach")
    else:
        print("✓ SIGNIFICANT: Luxembourg has HIGHER reach")
else:
    print("✗ Not significant")

channel_summary = all_df.groupby(['country', 'channel_name']).agg({
    'video_title': 'count',
    'view_count': ['sum', 'mean'],
    'engagement_rate': 'mean',
    'is_multilingual': 'mean'
}).reset_index()

channel_summary.columns = ['country', 'channel', 'total_videos', 'total_views', 'avg_views', 'avg_engagement', 'multilingual_rate']

print("\n" + "="*70)
print("TOP 5 LUXEMBOURG INFLUENCERS")
print("="*70)
top5_lux = channel_summary[channel_summary['country']=='Luxembourg'].nlargest(5, 'total_views')
for idx, row in top5_lux.iterrows():
    print(f"{row['channel']}")
    print(f"  Views: {row['total_views']:,.0f} | Videos: {row['total_videos']:.0f} | Engagement: {row['avg_engagement']:.4f} | Multilingual: {row['multilingual_rate']:.1%}")

all_df.to_excel('final_dataset_corrected.xlsx', index=False)
channel_summary.to_excel('channel_summary_corrected.xlsx', index=False)

print("\n" + "="*70)
print("Files saved!")
print("="*70)