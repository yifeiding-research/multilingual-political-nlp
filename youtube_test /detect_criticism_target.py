import pandas as pd
from transformers import pipeline
import re

all_df = pd.read_excel('./complete_dataset_with_sentiment.xlsx')
hu_df = all_df[all_df['country']=='Hungary'].copy()

print("="*70)
print("DETECTING CRITICISM TARGETS IN HUNGARY")
print("="*70)

government_keywords = [
    'orbán', 'fidesz', 'kormány', 'miniszter', 'government', 
    'minister', 'ruling', 'hatalom', 'власть'
]

opposition_keywords = [
    'ellenzék', 'opposition', 'gyurcsány', 'márki-zay', 'karácsony',
    'momentum', 'dk', 'jobbik', 'lmp', 'párbeszéd', 'tisza'
]

def detect_target(text):
    text_lower = str(text).lower()
    
    has_gov = any(keyword in text_lower for keyword in government_keywords)
    has_opp = any(keyword in text_lower for keyword in opposition_keywords)
    
    if has_gov and not has_opp:
        return 'targets_government'
    elif has_opp and not has_gov:
        return 'targets_opposition'
    elif has_gov and has_opp:
        return 'targets_both'
    else:
        return 'unclear'

print("\nAnalyzing criticism targets...")

hu_df['criticism_target'] = hu_df['video_title'].apply(detect_target)

hu_critical = hu_df[hu_df['sentiment'] == 'critical'].copy()

print("\n" + "="*70)
print("CRITICISM TARGET ANALYSIS (Critical videos only)")
print("="*70)

target_counts = hu_critical['criticism_target'].value_counts()
print("\nOverall distribution:")
for target, count in target_counts.items():
    pct = count / len(hu_critical) * 100
    print(f"  {target}: {count} ({pct:.1f}%)")

print("\n" + "="*70)
print("BY POLITICAL STANCE")
print("="*70)

pro_government = ['M1 - Híradó', 'hirado․hu - Magyarország hírforrása', 'Hit Rádió']
opposition = ['Telex․hu', 'Kontroll', 'Dr. Márki-Zay Péter', 'A TISZA TÁMOGATÓI KÖZÖSSÉG']
independent = ['DW Magyar', 'Magyar Közöny Podcast', 'Mandiner']

hu_df['political_stance'] = 'other'
hu_df.loc[hu_df['channel_name'].isin(pro_government), 'political_stance'] = 'pro_government'
hu_df.loc[hu_df['channel_name'].isin(opposition), 'political_stance'] = 'opposition'
hu_df.loc[hu_df['channel_name'].isin(independent), 'political_stance'] = 'independent'

hu_critical_stance = hu_df[(hu_df['sentiment'] == 'critical')].copy()

stance_target = pd.crosstab(
    hu_critical_stance['political_stance'],
    hu_critical_stance['criticism_target'],
    normalize='index'
) * 100

print("\nCriticism targets by channel stance (%):")
print(stance_target)

print("\n" + "="*70)
print("REVISED H2 ANALYSIS")
print("="*70)

pro_gov_crit_gov = hu_df[
    (hu_df['political_stance']=='pro_government') & 
    (hu_df['sentiment']=='critical') & 
    (hu_df['criticism_target']=='targets_government')
]

opp_crit_gov = hu_df[
    (hu_df['political_stance']=='opposition') & 
    (hu_df['sentiment']=='critical') & 
    (hu_df['criticism_target']=='targets_government')
]

pro_gov_total = len(hu_df[hu_df['political_stance']=='pro_government'])
opp_total = len(hu_df[hu_df['political_stance']=='opposition'])

pro_gov_crit_gov_pct = len(pro_gov_crit_gov) / pro_gov_total * 100
opp_crit_gov_pct = len(opp_crit_gov) / opp_total * 100

print(f"\nPro-government channels criticizing government: {pro_gov_crit_gov_pct:.2f}%")
print(f"Opposition channels criticizing government: {opp_crit_gov_pct:.2f}%")

print("\n" + "="*70)
print("COMPARISON WITH FRANCE AND LUXEMBOURG")
print("="*70)

fr_df = all_df[all_df['country']=='France'].copy()
lux_df = all_df[all_df['country']=='Luxembourg'].copy()

fr_gov_keywords = ['macron', 'gouvernement', 'ministre', 'borne', 'attal']
lux_gov_keywords = ['bettel', 'frieden', 'gouvernement', 'regierung', 'ministre']

def detect_gov_criticism_fr(text):
    text_lower = str(text).lower()
    return any(keyword in text_lower for keyword in fr_gov_keywords)

def detect_gov_criticism_lux(text):
    text_lower = str(text).lower()
    return any(keyword in text_lower for keyword in lux_gov_keywords)

fr_critical = fr_df[fr_df['sentiment']=='critical'].copy()
lux_critical = lux_df[lux_df['sentiment']=='critical'].copy()

fr_critical['targets_government'] = fr_critical['video_title'].apply(detect_gov_criticism_fr)
lux_critical['targets_government'] = lux_critical['video_title'].apply(detect_gov_criticism_lux)
hu_critical['targets_government'] = hu_critical['criticism_target'].isin(['targets_government', 'targets_both'])

fr_gov_crit_pct = fr_critical['targets_government'].mean() * 100
lux_gov_crit_pct = lux_critical['targets_government'].mean() * 100
hu_gov_crit_pct = hu_critical['targets_government'].mean() * 100

print(f"\n% of critical videos targeting government:")
print(f"Luxembourg: {lux_gov_crit_pct:.2f}%")
print(f"France: {fr_gov_crit_pct:.2f}%")
print(f"Hungary: {hu_gov_crit_pct:.2f}%")

from scipy import stats

contingency = [
    [sum(lux_critical['targets_government']), sum(~lux_critical['targets_government'])],
    [sum(fr_critical['targets_government']), sum(~fr_critical['targets_government'])],
    [sum(hu_critical['targets_government']), sum(~hu_critical['targets_government'])]
]

chi2, p_value = stats.chi2_contingency(contingency)[:2]

print(f"\nChi-square test: p = {p_value:.6f}")
if p_value < 0.05:
    if hu_gov_crit_pct < fr_gov_crit_pct and hu_gov_crit_pct < lux_gov_crit_pct:
        print("✓ SIGNIFICANT: Hungary has LOWER government criticism")
        print("✓ H2 SUPPORTED with target detection!")
    else:
        print("✓ Significant difference exists")
else:
    print("✗ Not significant")

import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

stance_target.plot(kind='bar', ax=axes[0], rot=45)
axes[0].set_ylabel('Percentage')
axes[0].set_title('Hungary: Criticism Targets by Channel Stance')
axes[0].legend(title='Target', bbox_to_anchor=(1.05, 1))

country_data = {
    'Luxembourg': lux_gov_crit_pct,
    'France': fr_gov_crit_pct,
    'Hungary': hu_gov_crit_pct
}

axes[1].bar(country_data.keys(), country_data.values(), color=['#3498db', '#e74c3c', '#2ecc71'])
axes[1].set_ylabel('% of Critical Videos')
axes[1].set_title('Government Criticism Rate by Country')
axes[1].set_ylim(0, max(country_data.values()) * 1.2)

for i, (country, value) in enumerate(country_data.items()):
    axes[1].text(i, value + 1, f'{value:.1f}%', ha='center', fontsize=12)

plt.tight_layout()
plt.savefig('criticism_target_analysis.png', dpi=300, bbox_inches='tight')

hu_df.to_excel('hungary_with_targets.xlsx', index=False)

print("\n" + "="*70)
print("Files saved:")
print("- criticism_target_analysis.png")
print("- hungary_with_targets.xlsx")
print("="*70)