import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

all_df = pd.read_excel('./complete_dataset_with_sentiment.xlsx')

hu_df = all_df[all_df['country']=='Hungary'].copy()

print("="*70)
print("HUNGARY CHANNEL ANALYSIS")
print("="*70)

hu_channel_sentiment = hu_df.groupby('channel_name')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100

hu_channel_summary = hu_df.groupby('channel_name').agg({
    'video_title': 'count',
    'view_count': 'sum',
    'sentiment': lambda x: (x == 'critical').mean() * 100
}).rename(columns={'video_title': 'videos', 'view_count': 'total_views', 'sentiment': 'critical_pct'})

hu_channel_summary = hu_channel_summary.sort_values('critical_pct', ascending=False)

print("\nHungary channels ranked by criticism rate:")
print(hu_channel_summary)

print("\n" + "="*70)
print("PRO-GOVERNMENT vs OPPOSITION CHANNELS (manual classification)")
print("="*70)

pro_government = ['M1 - Híradó', 'hirado․hu - Magyarország hírforrása', 'Hit Rádió']
opposition = ['Telex․hu', 'Kontroll', 'Dr. Márki-Zay Péter', 'A TISZA TÁMOGATÓI KÖZÖSSÉG']
independent = ['DW Magyar', 'Magyar Közöny Podcast', 'Mandiner']

hu_df['political_stance'] = 'other'
hu_df.loc[hu_df['channel_name'].isin(pro_government), 'political_stance'] = 'pro_government'
hu_df.loc[hu_df['channel_name'].isin(opposition), 'political_stance'] = 'opposition'
hu_df.loc[hu_df['channel_name'].isin(independent), 'political_stance'] = 'independent'

stance_sentiment = hu_df.groupby('political_stance')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100

print("\nSentiment by political stance:")
print(stance_sentiment)

pro_gov_crit = (hu_df[hu_df['political_stance']=='pro_government']['sentiment'] == 'critical').mean()
opp_crit = (hu_df[hu_df['political_stance']=='opposition']['sentiment'] == 'critical').mean()

print(f"\nPro-government channels critical rate: {pro_gov_crit:.2%}")
print(f"Opposition channels critical rate: {opp_crit:.2%}")

hu_df['published_month'] = pd.to_datetime(hu_df['published_date']).dt.to_period('M')

monthly_sentiment = hu_df.groupby(['published_month', 'sentiment']).size().unstack(fill_value=0)
monthly_sentiment['critical_pct'] = monthly_sentiment['critical'] / monthly_sentiment.sum(axis=1) * 100

print("\n" + "="*70)
print("TEMPORAL ANALYSIS (by month)")
print("="*70)
print(monthly_sentiment[['critical', 'neutral', 'supportive', 'critical_pct']])

print("\n" + "="*70)
print("CROSS-COUNTRY COMPARISON BY CHANNEL TYPE")
print("="*70)

fr_df = all_df[all_df['country']=='France'].copy()
lux_df = all_df[all_df['country']=='Luxembourg'].copy()

fr_media = ['FRANCE 24', 'BFMTV', 'TF1 INFO', 'LCI', 'RFI']
fr_politicians = ['JEAN-LUC MÉLENCHON']
fr_independent = ['HugoDécrypte - Actus du jour', 'Pure Politique']

lux_parties = ['CSV - Chrëschtlech-Sozial Vollekspartei', 'Demokratesch Partei', 'LSAP', 'déi gréng', 'Alternativ Demokratesch Reformpartei']
lux_media = ['Paperjam', 'Tageblatt Lëtzebuerg', 'Luxemburger Wort']

fr_df['channel_type'] = 'other'
fr_df.loc[fr_df['channel_name'].isin(fr_media), 'channel_type'] = 'media'
fr_df.loc[fr_df['channel_name'].isin(fr_politicians), 'channel_type'] = 'politician'
fr_df.loc[fr_df['channel_name'].isin(fr_independent), 'channel_type'] = 'independent'

lux_df['channel_type'] = 'other'
lux_df.loc[lux_df['channel_name'].isin(lux_parties), 'channel_type'] = 'party'
lux_df.loc[lux_df['channel_name'].isin(lux_media), 'channel_type'] = 'media'

hu_df['channel_type'] = 'other'
hu_df.loc[hu_df['political_stance']=='pro_government', 'channel_type'] = 'pro_gov'
hu_df.loc[hu_df['political_stance']=='opposition', 'channel_type'] = 'opposition'

print("\nFrance channel types:")
print(fr_df.groupby('channel_type')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100)

print("\nLuxembourg channel types:")
print(lux_df.groupby('channel_type')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100)

print("\nHungary channel types:")
print(hu_df.groupby('channel_type')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

hu_channel_summary.nlargest(15, 'critical_pct')['critical_pct'].plot(
    kind='barh', ax=axes[0,0], color='#e74c3c'
)
axes[0,0].set_xlabel('Critical Content %')
axes[0,0].set_title('Hungary: Top 15 Channels by Criticism Rate')
axes[0,0].invert_yaxis()

stance_sentiment.T.plot(kind='bar', ax=axes[0,1], rot=0)
axes[0,1].set_ylabel('Percentage')
axes[0,1].set_title('Hungary: Sentiment by Political Stance')
axes[0,1].legend(title='Stance')

monthly_sentiment['critical_pct'].plot(ax=axes[1,0], marker='o', linewidth=2, color='#3498db')
axes[1,0].set_ylabel('Critical Content %')
axes[1,0].set_xlabel('Month')
axes[1,0].set_title('Hungary: Criticism Rate Over Time')
axes[1,0].grid(True, alpha=0.3)

comparison_data = {
    'Luxembourg': lux_df['sentiment'].value_counts(normalize=True) * 100,
    'France': fr_df['sentiment'].value_counts(normalize=True) * 100,
    'Hungary': hu_df['sentiment'].value_counts(normalize=True) * 100
}
comparison_df = pd.DataFrame(comparison_data).T

comparison_df.plot(kind='bar', ax=axes[1,1], rot=0)
axes[1,1].set_ylabel('Percentage')
axes[1,1].set_title('Sentiment Distribution by Country')
axes[1,1].legend(title='Sentiment')

plt.tight_layout()
plt.savefig('h2_failure_analysis.png', dpi=300, bbox_inches='tight')

hu_channel_sentiment.to_excel('hungary_channel_sentiment.xlsx')
stance_sentiment.to_excel('hungary_stance_sentiment.xlsx')

print("\n" + "="*70)
print("Files saved:")
print("- h2_failure_analysis.png")
print("- hungary_channel_sentiment.xlsx")
print("- hungary_stance_sentiment.xlsx")
print("="*70)