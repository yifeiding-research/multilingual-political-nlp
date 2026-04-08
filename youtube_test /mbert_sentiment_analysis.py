import pandas as pd
from transformers import pipeline
import torch

lux_df = pd.read_excel('./political_influencers_Luxembourg_FINAL.xlsx')
fr_df = pd.read_excel('./political_influencers_France.xlsx')
hu_df = pd.read_excel('./political_influencers_Hungary.xlsx')

all_df = pd.concat([lux_df, fr_df, hu_df])

print("="*70)
print("Loading mBERT sentiment model...")
print("="*70)

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",
    device=0 if torch.cuda.is_available() else -1
)

def analyze_sentiment(text):
    try:
        result = sentiment_analyzer(str(text)[:512])[0]
        score = int(result['label'].split()[0])
        
        if score <= 2:
            return 'critical'
        elif score == 3:
            return 'neutral'
        else:
            return 'supportive'
    except:
        return 'neutral'

print("\nAnalyzing sentiment for all videos...")
print("This may take 10-20 minutes...\n")

total = len(all_df)
for idx, row in all_df.iterrows():
    if idx % 100 == 0:
        print(f"Progress: {idx}/{total} ({idx/total*100:.1f}%)")
    all_df.at[idx, 'sentiment'] = analyze_sentiment(row['video_title'])

print("\n" + "="*70)
print("H2: DEMOCRATIC CRITICISM HYPOTHESIS")
print("="*70)

lux_crit = (all_df[all_df['country']=='Luxembourg']['sentiment'] == 'critical').mean()
fr_crit = (all_df[all_df['country']=='France']['sentiment'] == 'critical').mean()
hu_crit = (all_df[all_df['country']=='Hungary']['sentiment'] == 'critical').mean()

print(f"\nCritical content rate:")
print(f"Luxembourg: {lux_crit:.2%}")
print(f"France: {fr_crit:.2%}")
print(f"Hungary: {hu_crit:.2%}")

print(f"\nSentiment distribution:")
for country in ['Luxembourg', 'France', 'Hungary']:
    country_df = all_df[all_df['country']==country]
    print(f"\n{country}:")
    sentiment_counts = country_df['sentiment'].value_counts()
    for sent, count in sentiment_counts.items():
        pct = count / len(country_df) * 100
        print(f"  {sent}: {count} ({pct:.1f}%)")

from scipy import stats

contingency_table = pd.crosstab(
    all_df['country'], 
    all_df['sentiment']
)
chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print(f"\nChi-square test:")
print(f"p-value: {p_value:.6f}")
if p_value < 0.05:
    print("✓ SIGNIFICANT: Countries differ in criticism levels")
    if hu_crit < fr_crit and hu_crit < lux_crit:
        print("✓ Hungary shows LOWER criticism (democratic backsliding effect)")
else:
    print("✗ Not significant")

all_df.to_excel('complete_dataset_with_sentiment.xlsx', index=False)

sentiment_summary = all_df.groupby('country')['sentiment'].value_counts(normalize=True).unstack(fill_value=0) * 100
sentiment_summary.to_excel('sentiment_summary.xlsx')

print("\n" + "="*70)
print("Files saved:")
print("- complete_dataset_with_sentiment.xlsx")
print("- sentiment_summary.xlsx")
print("="*70)