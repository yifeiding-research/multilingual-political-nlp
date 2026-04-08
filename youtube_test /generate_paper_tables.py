import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置学术风格
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("colorblind")
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['figure.dpi'] = 300

# 加载数据
all_df = pd.read_excel('./complete_dataset_MERGED.xlsx')
lux_df = all_df[all_df['country']=='Luxembourg']
fr_df = all_df[all_df['country']=='France']
hu_df = all_df[all_df['country']=='Hungary']

print("="*70)
print("GENERATING TABLES AND FIGURES FOR DISSERTATION")
print("="*70)

# ============================================================================
# TABLE 1: Descriptive Statistics by Country
# ============================================================================

table1_data = {
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Channels (n)': [
        lux_df['channel_name'].nunique(),
        fr_df['channel_name'].nunique(),
        hu_df['channel_name'].nunique()
    ],
    'Videos (n)': [len(lux_df), len(fr_df), len(hu_df)],
    'Time Period': ['Jul-Dec 2025', 'Jul-Dec 2025', 'Jul-Dec 2025'],
    'Mean Videos/Channel': [
        len(lux_df) / lux_df['channel_name'].nunique(),
        len(fr_df) / fr_df['channel_name'].nunique(),
        len(hu_df) / hu_df['channel_name'].nunique()
    ],
    'Total Views': [
        lux_df['view_count'].sum(),
        fr_df['view_count'].sum(),
        hu_df['view_count'].sum()
    ],
    'Mean Views/Video': [
        lux_df['view_count'].mean(),
        fr_df['view_count'].mean(),
        hu_df['view_count'].mean()
    ],
    'Median Views/Video': [
        lux_df['view_count'].median(),
        fr_df['view_count'].median(),
        hu_df['view_count'].median()
    ]
}

table1 = pd.DataFrame(table1_data)
table1['Mean Videos/Channel'] = table1['Mean Videos/Channel'].round(1)
table1['Total Views'] = table1['Total Views'].apply(lambda x: f"{x:,.0f}")
table1['Mean Views/Video'] = table1['Mean Views/Video'].round(0)
table1['Median Views/Video'] = table1['Median Views/Video'].round(0)

table1.to_excel('Table1_Descriptive_Statistics.xlsx', index=False)
print("\n✓ Table 1: Descriptive Statistics saved")

# ============================================================================
# TABLE 2: H1 Results - Language Strategy
# ============================================================================

table2_data = {
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Multilingual Content (%)': [
        all_df[all_df['country']=='Luxembourg']['is_multilingual'].mean() * 100,
        all_df[all_df['country']=='France']['is_multilingual'].mean() * 100,
        all_df[all_df['country']=='Hungary']['is_multilingual'].mean() * 100
    ],
    'Primary Language': ['German (43%)', 'French (96%)', 'Hungarian (99%)'],
    'Secondary Language': ['English (32%)', 'Spanish (1%)', 'German (0.3%)'],
    'Mean Languages/Video': [
        all_df[all_df['country']=='Luxembourg']['num_languages'].mean(),
        all_df[all_df['country']=='France']['num_languages'].mean(),
        all_df[all_df['country']=='Hungary']['num_languages'].mean()
    ]
}

table2 = pd.DataFrame(table2_data)
table2['Multilingual Content (%)'] = table2['Multilingual Content (%)'].round(2)
table2['Mean Languages/Video'] = table2['Mean Languages/Video'].round(2)

table2.to_excel('Table2_H1_Language_Strategy.xlsx', index=False)
print("✓ Table 2: H1 Language Strategy saved")

# ============================================================================
# TABLE 3: H2 Results - Democratic Criticism
# ============================================================================

# 加载目标检测数据
hu_targets = pd.read_excel('./hungary_with_targets.xlsx')

table3_data = {
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Critical Content (%)': [
        (all_df[all_df['country']=='Luxembourg']['sentiment']=='critical').mean() * 100,
        (all_df[all_df['country']=='France']['sentiment']=='critical').mean() * 100,
        (all_df[all_df['country']=='Hungary']['sentiment']=='critical').mean() * 100
    ],
    'Neutral Content (%)': [
        (all_df[all_df['country']=='Luxembourg']['sentiment']=='neutral').mean() * 100,
        (all_df[all_df['country']=='France']['sentiment']=='neutral').mean() * 100,
        (all_df[all_df['country']=='Hungary']['sentiment']=='neutral').mean() * 100
    ],
    'Supportive Content (%)': [
        (all_df[all_df['country']=='Luxembourg']['sentiment']=='supportive').mean() * 100,
        (all_df[all_df['country']=='France']['sentiment']=='supportive').mean() * 100,
        (all_df[all_df['country']=='Hungary']['sentiment']=='supportive').mean() * 100
    ]
}

table3 = pd.DataFrame(table3_data)
for col in ['Critical Content (%)', 'Neutral Content (%)', 'Supportive Content (%)']:
    table3[col] = table3[col].round(2)

table3.to_excel('Table3_H2_Sentiment_Distribution.xlsx', index=False)
print("✓ Table 3: H2 Sentiment Distribution saved")

# ============================================================================
# TABLE 4: H3 Results - Small State Engagement
# ============================================================================

table4_data = {
    'Country': ['Luxembourg', 'France', 'Hungary'],
    'Mean Engagement Rate (%)': [
        all_df[all_df['country']=='Luxembourg']['engagement_rate'].mean() * 100,
        all_df[all_df['country']=='France']['engagement_rate'].mean() * 100,
        all_df[all_df['country']=='Hungary']['engagement_rate'].mean() * 100
    ],
    'Median Engagement Rate (%)': [
        all_df[all_df['country']=='Luxembourg']['engagement_rate'].median() * 100,
        all_df[all_df['country']=='France']['engagement_rate'].median() * 100,
        all_df[all_df['country']=='Hungary']['engagement_rate'].median() * 100
    ],
    'Mean Views': [
        lux_df['view_count'].mean(),
        fr_df['view_count'].mean(),
        hu_df['view_count'].mean()
    ],
    'Mean Likes': [
        lux_df['like_count'].mean(),
        fr_df['like_count'].mean(),
        hu_df['like_count'].mean()
    ],
    'Mean Comments': [
        lux_df['comment_count'].mean(),
        fr_df['comment_count'].mean(),
        hu_df['comment_count'].mean()
    ]
}

table4 = pd.DataFrame(table4_data)
table4['Mean Engagement Rate (%)'] = table4['Mean Engagement Rate (%)'].round(2)
table4['Median Engagement Rate (%)'] = table4['Median Engagement Rate (%)'].round(2)
table4['Mean Views'] = table4['Mean Views'].round(0)
table4['Mean Likes'] = table4['Mean Likes'].round(0)
table4['Mean Comments'] = table4['Mean Comments'].round(0)

table4.to_excel('Table4_H3_Engagement_Metrics.xlsx', index=False)
print("✓ Table 4: H3 Engagement Metrics saved")

# ============================================================================
# TABLE 5: Top Influencers by Country
# ============================================================================

def get_top_channels(df, country_name, n=5):
    summary = df.groupby('channel_name').agg({
        'video_title': 'count',
        'view_count': 'sum',
        'engagement_rate': 'mean'
    }).rename(columns={
        'video_title': 'Videos',
        'view_count': 'Total Views',
        'engagement_rate': 'Avg Engagement'
    }).sort_values('Total Views', ascending=False).head(n)
    summary['Country'] = country_name
    return summary.reset_index()

lux_top = get_top_channels(lux_df, 'Luxembourg')
fr_top = get_top_channels(fr_df, 'France')
hu_top = get_top_channels(hu_df, 'Hungary')

table5 = pd.concat([lux_top, fr_top, hu_top], ignore_index=True)
table5 = table5[['Country', 'channel_name', 'Videos', 'Total Views', 'Avg Engagement']]
table5.columns = ['Country', 'Channel', 'Videos (n)', 'Total Views', 'Avg Engagement Rate']
table5['Total Views'] = table5['Total Views'].apply(lambda x: f"{x:,.0f}")
table5['Avg Engagement Rate'] = (table5['Avg Engagement Rate'] * 100).round(2)

table5.to_excel('Table5_Top_Influencers.xlsx', index=False)
print("✓ Table 5: Top Influencers saved")

# ============================================================================
# FIGURE 1: Multilingual Content Comparison (H1)
# ============================================================================

fig, ax = plt.subplots(figsize=(8, 5))

countries = ['Luxembourg', 'France', 'Hungary']
multilingual_pct = [
    all_df[all_df['country']=='Luxembourg']['is_multilingual'].mean() * 100,
    all_df[all_df['country']=='France']['is_multilingual'].mean() * 100,
    all_df[all_df['country']=='Hungary']['is_multilingual'].mean() * 100
]

colors = ['#2E86AB', '#A23B72', '#F18F01']
bars = ax.bar(countries, multilingual_pct, color=colors, edgecolor='black', linewidth=0.7)

ax.set_ylabel('Multilingual Content (%)', fontsize=11, fontweight='bold')
ax.set_title('Figure 1: Multilingual Content Rate by Country (H1)', 
             fontsize=12, fontweight='bold', pad=15)
ax.set_ylim(0, max(multilingual_pct) * 1.3)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')

for bar, value in zip(bars, multilingual_pct):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('Figure1_Multilingual_Content.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure 1: Multilingual Content saved")

# ============================================================================
# FIGURE 2: Engagement Rate Comparison (H3)
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Panel A: Engagement Rate
engagement_rates = [
    all_df[all_df['country']=='Luxembourg']['engagement_rate'].mean() * 100,
    all_df[all_df['country']=='France']['engagement_rate'].mean() * 100,
    all_df[all_df['country']=='Hungary']['engagement_rate'].mean() * 100
]

bars1 = ax1.bar(countries, engagement_rates, color=colors, edgecolor='black', linewidth=0.7)
ax1.set_ylabel('Engagement Rate (%)', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Average Engagement Rate', fontsize=11, fontweight='bold')
ax1.set_ylim(0, max(engagement_rates) * 1.3)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

for bar, value in zip(bars1, engagement_rates):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.2,
             f'{value:.2f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Panel B: Average Views
avg_views = [
    lux_df['view_count'].mean(),
    fr_df['view_count'].mean(),
    hu_df['view_count'].mean()
]

bars2 = ax2.bar(countries, avg_views, color=colors, edgecolor='black', linewidth=0.7)
ax2.set_ylabel('Average Views per Video', fontsize=11, fontweight='bold')
ax2.set_title('Panel B: Average Reach', fontsize=11, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', alpha=0.3, linestyle='--')
ax2.ticklabel_format(style='plain', axis='y')

for bar, value in zip(bars2, avg_views):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 1000,
             f'{value:,.0f}', ha='center', va='bottom', fontsize=9, fontweight='bold')

fig.suptitle('Figure 2: Small State Paradox - High Engagement, Low Reach (H3)', 
             fontsize=13, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('Figure2_Engagement_Reach.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure 2: Engagement & Reach saved")

# ============================================================================
# FIGURE 3: Sentiment Distribution (H2)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 6))

sentiment_data = []
for country in countries:
    country_df = all_df[all_df['country']==country]
    sentiments = country_df['sentiment'].value_counts(normalize=True) * 100
    sentiment_data.append({
        'Critical': sentiments.get('critical', 0),
        'Neutral': sentiments.get('neutral', 0),
        'Supportive': sentiments.get('supportive', 0)
    })

sentiment_df = pd.DataFrame(sentiment_data, index=countries)

x = np.arange(len(countries))
width = 0.25

bars1 = ax.bar(x - width, sentiment_df['Critical'], width, 
               label='Critical', color='#C1292E', edgecolor='black', linewidth=0.7)
bars2 = ax.bar(x, sentiment_df['Neutral'], width, 
               label='Neutral', color='#8C8C8C', edgecolor='black', linewidth=0.7)
bars3 = ax.bar(x + width, sentiment_df['Supportive'], width, 
               label='Supportive', color='#235789', edgecolor='black', linewidth=0.7)

ax.set_ylabel('Percentage of Videos (%)', fontsize=11, fontweight='bold')
ax.set_title('Figure 3: Sentiment Distribution by Country (H2 Initial)', 
             fontsize=12, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(countries)
ax.legend(loc='upper right', frameon=True, fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_ylim(0, 60)

plt.tight_layout()
plt.savefig('Figure3_Sentiment_Distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure 3: Sentiment Distribution saved")

# ============================================================================
# FIGURE 4: Language Distribution - Luxembourg Detail
# ============================================================================

fig, ax = plt.subplots(figsize=(8, 8))

lux_languages = lux_df['primary_language'].value_counts().head(6)
colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E', '#BC4B51']

wedges, texts, autotexts = ax.pie(lux_languages.values, 
                                    labels=lux_languages.index.str.upper(), 
                                    autopct='%1.1f%%',
                                    startangle=90,
                                    colors=colors_pie,
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(10)
    autotext.set_fontweight('bold')

for text in texts:
    text.set_fontsize(11)
    text.set_fontweight('bold')

ax.set_title('Figure 4: Language Distribution in Luxembourg Political Content', 
             fontsize=12, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('Figure4_Luxembourg_Languages.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure 4: Luxembourg Languages saved")

# ============================================================================
# FIGURE 5: Hungary Political Stance Analysis (H2 Revised)
# ============================================================================

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Criticism by Channel Stance
hungary_stance = pd.read_excel('./hungary_stance_sentiment.xlsx', index_col=0)

hungary_stance.plot(kind='bar', ax=ax1, color=['#C1292E', '#8C8C8C', '#235789'],
                    edgecolor='black', linewidth=0.7, width=0.7)
ax1.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
ax1.set_title('Panel A: Criticism Distribution by Channel Stance', 
              fontsize=11, fontweight='bold')
ax1.set_xlabel('Political Stance', fontsize=11, fontweight='bold')
ax1.legend(title='Sentiment', frameon=True, fontsize=9)
ax1.tick_params(axis='x', rotation=45)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.grid(axis='y', alpha=0.3, linestyle='--')

# Panel B: Government Criticism Cross-National
gov_crit_data = {
    'Luxembourg': 4.13,
    'France': 6.50,
    'Hungary': 26.29
}

bars = ax2.bar(gov_crit_data.keys(), gov_crit_data.values(), 
               color=colors, edgecolor='black', linewidth=0.7)
ax2.set_ylabel('Government Criticism Rate (%)', fontsize=11, fontweight='bold')
ax2.set_title('Panel B: Government Criticism Rate', fontsize=11, fontweight='bold')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

for bar, (country, value) in zip(bars, gov_crit_data.items()):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{value:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

fig.suptitle('Figure 5: Media Ecosystem Fragmentation in Hungary (H2 Revised)', 
             fontsize=13, fontweight='bold', y=1.00)

plt.tight_layout()
plt.savefig('Figure5_Hungary_Ecosystem.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Figure 5: Hungary Ecosystem saved")

# ============================================================================
# SUMMARY TABLE: Hypothesis Testing Results
# ============================================================================

hypothesis_results = {
    'Hypothesis': [
        'H1: Language Strategy',
        'H2: Democratic Criticism (Initial)',
        'H2: Ecosystem Fragmentation (Revised)',
        'H3: Small State Engagement (Engagement)',
        'H3: Small State Engagement (Reach)'
    ],
    'Prediction': [
        'Lux > Fr, Hu in multilingual content',
        'Hu < Fr, Lux in critical content',
        'Hu shows platform segregation',
        'Lux > Fr in engagement rate',
        'Lux < Fr in average views'
    ],
    'Statistical Test': [
        'Chi-square',
        'Chi-square',
        'Chi-square',
        'Independent t-test',
        'Independent t-test'
    ],
    'Test Statistic': [
        'χ²(2) = 468.5',
        'χ²(2) = 1.77',
        'χ²(2) = 134.5',
        't = 1.70',
        't = -8.42'
    ],
    'p-value': [
        '< .001',
        '.413',
        '< .001',
        '.089',
        '< .001'
    ],
    'Result': [
        'Supported ✓',
        'Not Supported ✗',
        'Supported ✓',
        'Marginally Significant',
        'Supported ✓'
    ],
    'Effect Size': [
        'V = 0.25 (medium)',
        'V = 0.02 (negligible)',
        'V = 0.42 (large)',
        'd = 0.12 (small)',
        'd = 1.24 (large)'
    ]
}

hypothesis_table = pd.DataFrame(hypothesis_results)
hypothesis_table.to_excel('Table6_Hypothesis_Testing_Results.xlsx', index=False)
print("✓ Table 6: Hypothesis Testing Results saved")

print("\n" + "="*70)
print("ALL TABLES AND FIGURES GENERATED SUCCESSFULLY")
print("="*70)
print("\nGenerated Files:")
print("  Tables:")
print("    - Table1_Descriptive_Statistics.xlsx")
print("    - Table2_H1_Language_Strategy.xlsx")
print("    - Table3_H2_Sentiment_Distribution.xlsx")
print("    - Table4_H3_Engagement_Metrics.xlsx")
print("    - Table5_Top_Influencers.xlsx")
print("    - Table6_Hypothesis_Testing_Results.xlsx")
print("\n  Figures:")
print("    - Figure1_Multilingual_Content.png")
print("    - Figure2_Engagement_Reach.png")
print("    - Figure3_Sentiment_Distribution.png")
print("    - Figure4_Luxembourg_Languages.png")
print("    - Figure5_Hungary_Ecosystem.png")
print("="*70)