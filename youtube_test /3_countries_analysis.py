import pandas as pd

lux_df = pd.read_excel('political_influencers_Luxembourg.xlsx')
fr_df = pd.read_excel('political_influencers_France.xlsx')
hu_df = pd.read_excel('political_influencers_Hungary.xlsx')

all_df = pd.concat([lux_df, fr_df, hu_df])

print("Total videos:", len(all_df))
print("\nVideos per country:")
print(all_df['country'].value_counts())

print("\nTop 10 channels by total views:")
top_channels = all_df.groupby(['country', 'channel_name'])['view_count'].sum().sort_values(ascending=False).head(10)
print(top_channels)

all_df.to_excel('all_countries_combined.xlsx', index=False)
print("\nCombined data saved!")
import pandas as pd
from langdetect import detect_langs
import matplotlib.pyplot as plt
import seaborn as sns

lux_df = pd.read_excel('political_influencers_Luxembourg.xlsx')
fr_df = pd.read_excel('political_influencers_France.xlsx')
hu_df = pd.read_excel('political_influencers_Hungary.xlsx')

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

all_df['language_analysis'] = all_df['video_title'].apply(detect_languages)
all_df['primary_language'] = all_df['language_analysis'].apply(lambda x: x['primary_language'])
all_df['is_multilingual'] = all_df['language_analysis'].apply(lambda x: x['is_multilingual'])
all_df['num_languages'] = all_df['language_analysis'].apply(lambda x: x['num_languages'])

all_df['engagement_rate'] = (all_df['like_count'] + all_df['comment_count']) / all_df['view_count'].replace(0, 1)

channel_summary = all_df.groupby(['country', 'channel_name']).agg({
    'video_title': 'count',
    'view_count': ['sum', 'mean'],
    'like_count': ['sum', 'mean'],
    'comment_count': ['sum', 'mean'],
    'engagement_rate': 'mean',
    'is_multilingual': 'mean',
    'num_languages': 'mean'
}).reset_index()

channel_summary.columns = ['country', 'channel', 'total_videos', 'total_views', 'avg_views', 
                           'total_likes', 'avg_likes', 'total_comments', 'avg_comments', 
                           'avg_engagement', 'multilingual_rate', 'avg_languages']

country_stats = all_df.groupby('country').agg({
    'view_count': ['mean', 'sum'],
    'like_count': ['mean', 'sum'],
    'comment_count': ['mean', 'sum'],
    'engagement_rate': 'mean',
    'is_multilingual': 'mean',
    'num_languages': 'mean'
}).round(4)

print("="*60)
print("H1: LANGUAGE STRATEGY HYPOTHESIS")
print("="*60)
print("\nMultilingual content percentage:")
for country in ['Luxembourg', 'France', 'Hungary']:
    rate = all_df[all_df['country']==country]['is_multilingual'].mean()
    print(f"{country}: {rate:.2%}")

print("\n" + "="*60)
print("H3: SMALL STATE ENGAGEMENT HYPOTHESIS")
print("="*60)
print("\nAverage engagement rate:")
for country in ['Luxembourg', 'France', 'Hungary']:
    rate = all_df[all_df['country']==country]['engagement_rate'].mean()
    print(f"{country}: {rate:.4f}")

print("\nAverage views per video:")
for country in ['Luxembourg', 'France', 'Hungary']:
    avg = all_df[all_df['country']==country]['view_count'].mean()
    print(f"{country}: {avg:,.0f}")

print("\n" + "="*60)
print("TOP 5 CHANNELS PER COUNTRY (by total views)")
print("="*60)
for country in ['Luxembourg', 'France', 'Hungary']:
    print(f"\n{country}:")
    top5 = channel_summary[channel_summary['country']==country].nlargest(5, 'total_views')
    for idx, row in top5.iterrows():
        print(f"  {row['channel']}: {row['total_views']:,.0f} views ({row['total_videos']:.0f} videos)")

language_dist = all_df.groupby(['country', 'primary_language']).size().reset_index(name='count')

channel_summary.to_excel('channel_analysis.xlsx', index=False)
country_stats.to_csv('country_statistics.csv')
all_df.to_excel('all_data_with_analysis.xlsx', index=False)

print("\n" + "="*60)
print("Files saved:")
print("- channel_analysis.xlsx")
print("- country_statistics.csv")
print("- all_data_with_analysis.xlsx")
print("="*60)
import pandas as pd
from langdetect import detect_langs
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

lux_df = pd.read_excel('political_influencers_Luxembourg.xlsx')
fr_df = pd.read_excel('political_influencers_France.xlsx')
hu_df = pd.read_excel('political_influencers_Hungary.xlsx')

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

channel_summary = all_df.groupby(['country', 'channel_name']).agg({
    'video_title': 'count',
    'view_count': ['sum', 'mean'],
    'like_count': ['sum', 'mean'],
    'comment_count': ['sum', 'mean'],
    'engagement_rate': 'mean',
    'is_multilingual': 'mean',
    'num_languages': 'mean'
}).reset_index()

channel_summary.columns = ['country', 'channel', 'total_videos', 'total_views', 'avg_views', 
                           'total_likes', 'avg_likes', 'total_comments', 'avg_comments', 
                           'avg_engagement', 'multilingual_rate', 'avg_languages']

print("\n" + "="*60)
print("H1: LANGUAGE STRATEGY HYPOTHESIS")
print("="*60)
lux_multi = all_df[all_df['country']=='Luxembourg']['is_multilingual'].mean()
fr_multi = all_df[all_df['country']=='France']['is_multilingual'].mean()
hu_multi = all_df[all_df['country']=='Hungary']['is_multilingual'].mean()

print(f"\nLuxembourg: {lux_multi:.2%}")
print(f"France: {fr_multi:.2%}")
print(f"Hungary: {hu_multi:.2%}")

chi2, p_value = stats.chi2_contingency([
    [sum(all_df[all_df['country']=='Luxembourg']['is_multilingual']), 
     sum(~all_df[all_df['country']=='Luxembourg']['is_multilingual'])],
    [sum(all_df[all_df['country']=='France']['is_multilingual']), 
     sum(~all_df[all_df['country']=='France']['is_multilingual'])]
])[:2]
print(f"\nChi-square test (Lux vs France): p = {p_value:.4f}")
if p_value < 0.05:
    print("✓ Statistically significant difference")
else:
    print("✗ No significant difference")

print("\n" + "="*60)
print("H3: SMALL STATE ENGAGEMENT HYPOTHESIS")
print("="*60)

lux_eng = all_df[all_df['country']=='Luxembourg']['engagement_rate'].mean()
fr_eng = all_df[all_df['country']=='France']['engagement_rate'].mean()
hu_eng = all_df[all_df['country']=='Hungary']['engagement_rate'].mean()

print(f"\nEngagement rate:")
print(f"Luxembourg: {lux_eng:.4f}")
print(f"France: {fr_eng:.4f}")
print(f"Hungary: {hu_eng:.4f}")

lux_views = all_df[all_df['country']=='Luxembourg']['view_count'].mean()
fr_views = all_df[all_df['country']=='France']['view_count'].mean()
hu_views = all_df[all_df['country']=='Hungary']['view_count'].mean()

print(f"\nAverage views:")
print(f"Luxembourg: {lux_views:,.0f}")
print(f"France: {fr_views:,.0f}")
print(f"Hungary: {hu_views:,.0f}")

t_stat, p_value = stats.ttest_ind(
    all_df[all_df['country']=='Luxembourg']['engagement_rate'].dropna(),
    all_df[all_df['country']=='France']['engagement_rate'].dropna()
)
print(f"\nT-test (Lux vs France engagement): p = {p_value:.4f}")
if p_value < 0.05:
    print("✓ Statistically significant difference")
else:
    print("✗ No significant difference")

print("\n" + "="*60)
print("TOP 5 CHANNELS PER COUNTRY")
print("="*60)
for country in ['Luxembourg', 'France', 'Hungary']:
    print(f"\n{country}:")
    top5 = channel_summary[channel_summary['country']==country].nlargest(5, 'total_views')
    for idx, row in top5.iterrows():
        print(f"  {row['channel']}: {row['total_views']:,.0f} views, {row['avg_engagement']:.4f} engagement")

plt.style.use('seaborn-v0_8-darkgrid')
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

multi_data = [lux_multi*100, fr_multi*100, hu_multi*100]
axes[0, 0].bar(['Luxembourg', 'France', 'Hungary'], multi_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 0].set_ylabel('Percentage (%)')
axes[0, 0].set_title('H1: Multilingual Content Rate')
axes[0, 0].set_ylim(0, max(multi_data)*1.2)
for i, v in enumerate(multi_data):
    axes[0, 0].text(i, v+1, f'{v:.1f}%', ha='center')

eng_data = [lux_eng*100, fr_eng*100, hu_eng*100]
axes[0, 1].bar(['Luxembourg', 'France', 'Hungary'], eng_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[0, 1].set_ylabel('Engagement Rate (%)')
axes[0, 1].set_title('H3: Engagement Rate by Country')
for i, v in enumerate(eng_data):
    axes[0, 1].text(i, v+0.1, f'{v:.2f}%', ha='center')

view_data = [lux_views, fr_views, hu_views]
axes[1, 0].bar(['Luxembourg', 'France', 'Hungary'], view_data, color=['#3498db', '#e74c3c', '#2ecc71'])
axes[1, 0].set_ylabel('Average Views')
axes[1, 0].set_title('H3: Average Views per Video')
axes[1, 0].ticklabel_format(style='plain', axis='y')
for i, v in enumerate(view_data):
    axes[1, 0].text(i, v+1000, f'{v:,.0f}', ha='center')

for country, color in zip(['Luxembourg', 'France', 'Hungary'], ['#3498db', '#e74c3c', '#2ecc71']):
    data = all_df[all_df['country']==country]['engagement_rate'].dropna()
    axes[1, 1].hist(data, bins=50, alpha=0.6, label=country, color=color)
axes[1, 1].set_xlabel('Engagement Rate')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].set_title('Engagement Rate Distribution')
axes[1, 1].legend()
axes[1, 1].set_xlim(0, 0.2)

plt.tight_layout()
plt.savefig('analysis_visualizations.png', dpi=300, bbox_inches='tight')
print("\n✓ Visualization saved: analysis_visualizations.png")

channel_summary.to_excel('channel_analysis.xlsx', index=False)
all_df.to_excel('all_data_with_analysis.xlsx', index=False)

summary_stats = pd.DataFrame({
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Total Videos': [len(lux_df), len(fr_df), len(hu_df)],
    'Multilingual %': [lux_multi*100, fr_multi*100, hu_multi*100],
    'Avg Engagement': [lux_eng*100, fr_eng*100, hu_eng*100],
    'Avg Views': [lux_views, fr_views, hu_views]
})
summary_stats.to_excel('summary_statistics.xlsx', index=False)

print("\n" + "="*60)
print("Files saved:")
print("- analysis_visualizations.png")
print("- channel_analysis.xlsx")
print("- all_data_with_analysis.xlsx")
print("- summary_statistics.xlsx")
print("="*60)