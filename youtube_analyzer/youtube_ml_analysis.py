import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
sns.set_style("whitegrid")

# Load data
print("Loading data...")
with open('youtube_collection_20260110.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

df = pd.DataFrame(data['channels'])
df['subscribers'] = pd.to_numeric(df['subscribers'], errors='coerce')
df['view_count'] = pd.to_numeric(df['view_count'], errors='coerce')
df['video_count'] = pd.to_numeric(df['video_count'], errors='coerce')

# Feature engineering
df['avg_views_per_video'] = df['view_count'] / df['video_count']
df['engagement_rate'] = df['view_count'] / (df['subscribers'] + 1)
df['log_subscribers'] = np.log1p(df['subscribers'])
df['log_views'] = np.log1p(df['view_count'])
df['log_videos'] = np.log1p(df['video_count'])

df['channel_heat_index'] = (
    (df['log_subscribers'] / df['log_subscribers'].max()) * 0.4 +
    (df['engagement_rate'] / df['engagement_rate'].max()) * 0.4 +
    (df['avg_views_per_video'] / df['avg_views_per_video'].max()) * 0.2
)

# Clustering
features = ['log_subscribers', 'log_views', 'log_videos', 'avg_views_per_video', 'engagement_rate']
X = df[features].fillna(0)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
df['cluster'] = kmeans.fit_predict(X_scaled)

# ===== HYPOTHESIS TESTING =====
print("\n" + "="*70)
print("HYPOTHESIS TESTING RESULTS")
print("="*70)

# H1
print("\nH1: Language Strategy")
lu_eng = df[df['country']=='LU']['engagement_rate'].mean()
mono_eng = df[df['country'].isin(['FR','HU'])]['engagement_rate'].mean()
print(f"  Monolingual: {mono_eng:.2f}")
print(f"  Multilingual: {lu_eng:.2f}")

# H2
print("\nH2: Democratic Quality")
strong = df[df['country'].isin(['FR','LU'])]['channel_heat_index'].mean()
declining = df[df['country']=='HU']['channel_heat_index'].mean()
print(f"  Strong: {strong:.4f}")
print(f"  Declining: {declining:.4f}")
print(f"  SUPPORTED: {strong > declining}")

# H3
print("\nH3: Small State Engagement")
lu_subs = df[df['country']=='LU']['subscribers'].mean()
fr_subs = df[df['country']=='FR']['subscribers'].mean()
lu_eng2 = df[df['country']=='LU']['engagement_rate'].mean()
fr_eng2 = df[df['country']=='FR']['engagement_rate'].mean()
print(f"  LU subs: {lu_subs:.0f}, FR subs: {fr_subs:.0f}")
print(f"  LU eng: {lu_eng2:.2f}, FR eng: {fr_eng2:.2f}")

# H5
print("\nH5: Language Platform Disadvantage")
lu_heat = df[df['country']=='LU']['channel_heat_index'].mean()
fr_heat = df[df['country']=='FR']['channel_heat_index'].mean()
hu_heat = df[df['country']=='HU']['channel_heat_index'].mean()
print(f"  LU: {lu_heat:.4f}, FR: {fr_heat:.4f}, HU: {hu_heat:.4f}")
print(f"  SUPPORTED: {lu_heat < fr_heat and lu_heat < hu_heat}")

# ===== CREATE VISUALIZATION =====
print("\nCreating visualization...")

plt.close('all')
fig = plt.figure(figsize=(18, 12))

# 1. H1
ax1 = fig.add_subplot(3, 3, 1)
ax1.bar(['Monolingual', 'Multilingual'], [mono_eng, lu_eng], color=['#45B7D1', '#FF6B6B'])
ax1.set_ylabel('Engagement')
ax1.text(0.5, 1.15, 'H1', transform=ax1.transAxes, ha='center', fontsize=14, fontweight='bold')

# 2. H2
ax2 = fig.add_subplot(3, 3, 2)
ax2.bar(['Declining', 'Strong'], [declining, strong], color=['#FF6B6B', '#45B7D1'])
ax2.set_ylabel('Heat Index')
ax2.text(0.5, 1.15, 'H2', transform=ax2.transAxes, ha='center', fontsize=14, fontweight='bold')

# 3. H3
ax3 = fig.add_subplot(3, 3, 3)
countries = ['LU', 'HU', 'FR']
eng_vals = [df[df['country']==c]['engagement_rate'].mean() for c in countries]
ax3.bar(countries, eng_vals, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
ax3.set_ylabel('Engagement')
ax3.text(0.5, 1.15, 'H3', transform=ax3.transAxes, ha='center', fontsize=14, fontweight='bold')

# 4. Sample
ax4 = fig.add_subplot(3, 3, 4)
counts = [len(df[df['country']==c]) for c in countries]
ax4.bar(countries, counts, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
ax4.set_ylabel('Count')
ax4.text(0.5, 1.15, 'Sample', transform=ax4.transAxes, ha='center', fontsize=14, fontweight='bold')

# 5. H5 Distribution
ax5 = fig.add_subplot(3, 3, 5)
for country, color in [('FR', '#45B7D1'), ('HU', '#4ECDC4'), ('LU', '#FF6B6B')]:
    data = df[df['country']==country]['channel_heat_index'].dropna()
    ax5.hist(data, alpha=0.5, label=country, bins=12, color=color)
ax5.set_xlabel('Heat Index')
ax5.legend()
ax5.text(0.5, 1.15, 'H5', transform=ax5.transAxes, ha='center', fontsize=14, fontweight='bold')

# 6. Subscribers
ax6 = fig.add_subplot(3, 3, 6)
for country, color in [('FR', '#45B7D1'), ('HU', '#4ECDC4'), ('LU', '#FF6B6B')]:
    data = df[df['country']==country]['log_subscribers'].dropna()
    ax6.scatter([country]*len(data), data, alpha=0.5, s=40, color=color)
ax6.set_ylabel('Subscribers')
ax6.text(0.5, 1.15, 'Scale', transform=ax6.transAxes, ha='center', fontsize=14, fontweight='bold')

# 7. Video vs Engagement
ax7 = fig.add_subplot(3, 3, 7)
for country, color in [('FR', '#45B7D1'), ('HU', '#4ECDC4'), ('LU', '#FF6B6B')]:
    subset = df[df['country']==country]
    ax7.scatter(subset['video_count'], subset['engagement_rate'], label=country, alpha=0.5, s=30, color=color)
ax7.set_xlabel('Videos')
ax7.set_ylabel('Engagement')
ax7.set_xscale('log')
ax7.legend()
ax7.text(0.5, 1.15, 'Video', transform=ax7.transAxes, ha='center', fontsize=14, fontweight='bold')

# 8. Country Stats
ax8 = fig.add_subplot(3, 3, 8)
country_stats = df.groupby('country')[['log_subscribers', 'engagement_rate']].mean()
country_stats_norm = (country_stats - country_stats.min()) / (country_stats.max() - country_stats.min())
x_pos = range(len(country_stats_norm))
width = 0.35
ax8.bar([p - width/2 for p in x_pos], country_stats_norm['log_subscribers'], width, label='Subs', color='#45B7D1')
ax8.bar([p + width/2 for p in x_pos], country_stats_norm['engagement_rate'], width, label='Eng', color='#FF6B6B')
ax8.set_xticks(x_pos)
ax8.set_xticklabels(country_stats_norm.index)
ax8.set_ylabel('Score')
ax8.legend()
ax8.text(0.5, 1.15, 'Stats', transform=ax8.transAxes, ha='center', fontsize=14, fontweight='bold')

# 9. Clusters
ax9 = fig.add_subplot(3, 3, 9)
cluster_country = pd.crosstab(df['cluster'], df['country'])
cluster_country.plot(kind='bar', ax=ax9, color=['#45B7D1', '#4ECDC4', '#FF6B6B'], width=0.8)
ax9.set_ylabel('Count')
ax9.set_xlabel('Cluster')
ax9.legend(title='Country', loc='upper right')
ax9.text(0.5, 1.15, 'Cluster', transform=ax9.transAxes, ha='center', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('academic_hypothesis_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ SAVED: academic_hypothesis_analysis.png")
plt.close('all')

# Save data
df.to_csv('academic_analysis_results.csv', index=False)
print("✓ SAVED: academic_analysis_results.csv")

print("\nDone!")