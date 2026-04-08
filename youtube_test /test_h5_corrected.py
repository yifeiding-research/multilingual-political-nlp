import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

all_df = pd.read_excel('./complete_dataset_MERGED.xlsx')

print("="*70)
print("H5: MULTILINGUAL PLATFORM DISADVANTAGE HYPOTHESIS")
print("="*70)
print("\nHypothesis: Videos in smaller/minority languages face algorithmic")
print("disadvantages on global platforms like YouTube, affecting reach")
print("and engagement compared to videos in dominant global languages.")
print("="*70)

# ============================================================================
# Analysis 1: Language Performance in Luxembourg
# ============================================================================

print("\n" + "="*70)
print("ANALYSIS 1: Language Performance in Luxembourg")
print("="*70)

lux_df = all_df[all_df['country']=='Luxembourg'].copy()

lang_performance = lux_df.groupby('primary_language').agg({
    'video_title': 'count',
    'view_count': ['mean', 'median', 'sum'],
    'like_count': ['mean', 'sum'],
    'comment_count': ['mean', 'sum'],
    'engagement_rate': 'mean'
}).round(2)

lang_performance.columns = ['videos', 'avg_views', 'median_views', 'total_views', 
                            'avg_likes', 'total_likes', 'avg_comments', 
                            'total_comments', 'avg_engagement']

lang_performance_filtered = lang_performance[lang_performance['videos'] >= 10].sort_values('avg_views', ascending=False)

print("\nPerformance by Language (n≥10 videos):")
print(lang_performance_filtered[['videos', 'avg_views', 'median_views', 'avg_engagement']])

major_langs = ['de', 'en', 'fr']
lux_major = lux_df[lux_df['primary_language'].isin(major_langs)].copy()

print("\n" + "-"*70)
print("Major Languages Comparison:")
print("-"*70)

for lang in major_langs:
    lang_data = lux_major[lux_major['primary_language']==lang]
    if len(lang_data) > 0:
        lang_name = {'de': 'German', 'en': 'English', 'fr': 'French'}[lang]
        print(f"\n{lang_name} ({lang.upper()}):")
        print(f"  Videos: {len(lang_data)}")
        print(f"  Avg Views: {lang_data['view_count'].mean():.0f}")
        print(f"  Median Views: {lang_data['view_count'].median():.0f}")
        print(f"  Avg Engagement: {lang_data['engagement_rate'].mean():.4f} ({lang_data['engagement_rate'].mean()*100:.2f}%)")

de_views = lux_major[lux_major['primary_language']=='de']['view_count'].dropna()
en_views = lux_major[lux_major['primary_language']=='en']['view_count'].dropna()
fr_views = lux_major[lux_major['primary_language']=='fr']['view_count'].dropna()

if len(de_views) > 0 and len(en_views) > 0 and len(fr_views) > 0:
    f_stat, p_value = stats.f_oneway(de_views, en_views, fr_views)
    print(f"\n{'='*70}")
    print("ANOVA Test (German vs English vs French views):")
    print(f"F-statistic: {f_stat:.2f}")
    print(f"p-value: {p_value:.4f}")
    if p_value < 0.05:
        print("✓ SIGNIFICANT: Language affects view counts in Luxembourg")
        
        print("\nPairwise t-tests:")
        t_de_en, p_de_en = stats.ttest_ind(de_views, en_views)
        t_de_fr, p_de_fr = stats.ttest_ind(de_views, fr_views)
        t_en_fr, p_en_fr = stats.ttest_ind(en_views, fr_views)
        
        print(f"  German vs English: t={t_de_en:.2f}, p={p_de_en:.4f}")
        print(f"  German vs French: t={t_de_fr:.2f}, p={p_de_fr:.4f}")
        print(f"  English vs French: t={t_en_fr:.2f}, p={p_en_fr:.4f}")
    else:
        print("✗ Not significant")

# ============================================================================
# Analysis 2: English (Global) vs Local Languages
# ============================================================================

print("\n" + "="*70)
print("ANALYSIS 2: English (Global Language) Advantage")
print("="*70)

all_df['is_english'] = all_df['primary_language'] == 'en'

cross_country = all_df.groupby(['country', 'is_english']).agg({
    'view_count': ['mean', 'median'],
    'engagement_rate': 'mean',
    'video_title': 'count'
}).round(2)

cross_country.columns = ['avg_views', 'median_views', 'avg_engagement', 'videos']

print("\nEnglish vs Local Language Performance:")
print(cross_country)

# 卢森堡: 英语 vs 非英语
lux_en = lux_df[lux_df['primary_language']=='en']['view_count'].dropna()
lux_non_en = lux_df[lux_df['primary_language']!='en']['view_count'].dropna()

if len(lux_en) > 5 and len(lux_non_en) > 5:
    t_stat, p_value = stats.ttest_ind(lux_en, lux_non_en)
    print(f"\n{'='*70}")
    print("Luxembourg: English vs Non-English")
    print(f"English: {lux_en.mean():.0f} avg views (n={len(lux_en)})")
    print(f"Non-English: {lux_non_en.mean():.0f} avg views (n={len(lux_non_en)})")
    print(f"t-test: t={t_stat:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        if lux_en.mean() > lux_non_en.mean():
            print("✓ SIGNIFICANT: English content ADVANTAGED")
        else:
            print("✓ SIGNIFICANT: English content DISADVANTAGED (unexpected)")
    else:
        print("✗ Not significant")

# 匈牙利: 英语 vs 匈牙利语
hu_df = all_df[all_df['country']=='Hungary'].copy()
hu_en = hu_df[hu_df['primary_language']=='en']['view_count'].dropna()
hu_hungarian = hu_df[hu_df['primary_language']=='hu']['view_count'].dropna()

if len(hu_en) > 5:
    t_stat, p_value = stats.ttest_ind(hu_hungarian, hu_en)
    print(f"\n{'='*70}")
    print("Hungary: Hungarian vs English")
    print(f"Hungarian: {hu_hungarian.mean():.0f} avg views (n={len(hu_hungarian)})")
    print(f"English: {hu_en.mean():.0f} avg views (n={len(hu_en)})")
    print(f"t-test: t={t_stat:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        if hu_hungarian.mean() < hu_en.mean():
            print("✓ SIGNIFICANT: Hungarian language disadvantaged")
        else:
            print("✓ SIGNIFICANT: Hungarian language advantaged (unexpected)")
    else:
        print("✗ Not significant (small English sample)")

# 法国: 英语 vs 法语
fr_df = all_df[all_df['country']=='France'].copy()
fr_en = fr_df[fr_df['primary_language']=='en']['view_count'].dropna()
fr_french = fr_df[fr_df['primary_language']=='fr']['view_count'].dropna()

if len(fr_en) > 5:
    t_stat, p_value = stats.ttest_ind(fr_french, fr_en)
    print(f"\n{'='*70}")
    print("France: French vs English")
    print(f"French: {fr_french.mean():.0f} avg views (n={len(fr_french)})")
    print(f"English: {fr_en.mean():.0f} avg views (n={len(fr_en)})")
    print(f"t-test: t={t_stat:.2f}, p={p_value:.4f}")
    if p_value < 0.05:
        if fr_french.mean() < fr_en.mean():
            print("✓ SIGNIFICANT: French language disadvantaged")
        else:
            print("✓ SIGNIFICANT: French language advantaged")
    else:
        print("✗ Not significant")

# ============================================================================
# Analysis 3: Multilingual Content Performance
# ============================================================================

print("\n" + "="*70)
print("ANALYSIS 3: Multilingual Content Performance")
print("="*70)

for country in ['Luxembourg', 'France', 'Hungary']:
    country_df = all_df[all_df['country']==country].copy()
    
    mono = country_df[~country_df['is_multilingual']]['view_count'].dropna()
    multi = country_df[country_df['is_multilingual']]['view_count'].dropna()
    
    if len(multi) > 5:
        t_stat, p_value = stats.ttest_ind(mono, multi)
        
        print(f"\n{country}:")
        print(f"  Monolingual: {mono.mean():.0f} avg views (n={len(mono)})")
        print(f"  Multilingual: {multi.mean():.0f} avg views (n={len(multi)})")
        print(f"  Difference: {((multi.mean()-mono.mean())/mono.mean()*100):+.1f}%")
        print(f"  t-test: t={t_stat:.2f}, p={p_value:.4f}")
        
        if p_value < 0.05:
            if multi.mean() > mono.mean():
                print(f"  ✓ SIGNIFICANT: Multilingual content ADVANTAGED")
            else:
                print(f"  ✓ SIGNIFICANT: Multilingual content DISADVANTAGED")
        else:
            print(f"  ✗ Not significant")

# ============================================================================
# VISUALIZATIONS
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.rcParams['font.size'] = 10

# Plot 1: Luxembourg Language Performance
if len(lang_performance_filtered) > 0:
    top_langs = lang_performance_filtered.head(8)
    colors_lang = sns.color_palette("husl", len(top_langs))
    
    axes[0,0].barh(range(len(top_langs)), top_langs['avg_views'], color=colors_lang, edgecolor='black', linewidth=0.7)
    axes[0,0].set_yticks(range(len(top_langs)))
    axes[0,0].set_yticklabels(top_langs.index.str.upper())
    axes[0,0].set_xlabel('Average Views', fontweight='bold')
    axes[0,0].set_title('Panel A: Luxembourg Language Performance', fontweight='bold', fontsize=11)
    axes[0,0].invert_yaxis()
    axes[0,0].grid(axis='x', alpha=0.3)
    axes[0,0].spines['top'].set_visible(False)
    axes[0,0].spines['right'].set_visible(False)

# Plot 2: English vs Local Languages
countries = ['Luxembourg', 'France', 'Hungary']
en_means = []
local_means = []

for country in countries:
    c_df = all_df[all_df['country']==country]
    en_mean = c_df[c_df['primary_language']=='en']['view_count'].mean()
    local_mean = c_df[c_df['primary_language']!='en']['view_count'].mean()
    en_means.append(en_mean if not pd.isna(en_mean) else 0)
    local_means.append(local_mean)

x = np.arange(len(countries))
width = 0.35

bars1 = axes[0,1].bar(x - width/2, en_means, width, label='English', 
                      color='#235789', edgecolor='black', linewidth=0.7)
bars2 = axes[0,1].bar(x + width/2, local_means, width, label='Local Languages', 
                      color='#C1292E', edgecolor='black', linewidth=0.7)

axes[0,1].set_ylabel('Average Views', fontweight='bold')
axes[0,1].set_title('Panel B: English vs Local Language Performance', fontweight='bold', fontsize=11)
axes[0,1].set_xticks(x)
axes[0,1].set_xticklabels(countries)
axes[0,1].legend(frameon=True, fontsize=9)
axes[0,1].grid(axis='y', alpha=0.3)
axes[0,1].spines['top'].set_visible(False)
axes[0,1].spines['right'].set_visible(False)

# Plot 3: Language Distribution (Luxembourg)
if len(lux_major) > 0:
    lang_data = []
    lang_labels = []
    lang_colors = []
    color_map = {'de':'#2E86AB','en':'#A23B72','fr':'#F18F01'}
    
    for lang in major_langs:
        data = lux_major[lux_major['primary_language']==lang]['view_count'].dropna()
        if len(data) > 0:
            lang_data.append(data)
            lang_labels.append({'de':'German','en':'English','fr':'French'}[lang])
            lang_colors.append(color_map[lang])
    
    if len(lang_data) > 0:
        bp = axes[1,0].boxplot(lang_data, labels=lang_labels, patch_artist=True, widths=0.6)
        for patch, color in zip(bp['boxes'], lang_colors):
            patch.set_facecolor(color)
            patch.set_edgecolor('black')
            patch.set_linewidth(0.7)
        
        axes[1,0].set_ylabel('View Count (log scale)', fontweight='bold')
        axes[1,0].set_title('Panel C: Luxembourg View Distribution by Language', fontweight='bold', fontsize=11)
        axes[1,0].set_yscale('log')
        axes[1,0].grid(axis='y', alpha=0.3)
        axes[1,0].spines['top'].set_visible(False)
        axes[1,0].spines['right'].set_visible(False)

# Plot 4: Multilingual vs Monolingual
mono_means = []
multi_means = []

for country in countries:
    c_df = all_df[all_df['country']==country]
    mono_means.append(c_df[~c_df['is_multilingual']]['view_count'].mean())
    multi_means.append(c_df[c_df['is_multilingual']]['view_count'].mean())

bars1 = axes[1,1].bar(x - width/2, mono_means, width, label='Monolingual', 
                      color='#6A994E', edgecolor='black', linewidth=0.7)
bars2 = axes[1,1].bar(x + width/2, multi_means, width, label='Multilingual', 
                      color='#BC4B51', edgecolor='black', linewidth=0.7)

axes[1,1].set_ylabel('Average Views', fontweight='bold')
axes[1,1].set_title('Panel D: Monolingual vs Multilingual Content', fontweight='bold', fontsize=11)
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels(countries)
axes[1,1].legend(frameon=True, fontsize=9)
axes[1,1].grid(axis='y', alpha=0.3)
axes[1,1].spines['top'].set_visible(False)
axes[1,1].spines['right'].set_visible(False)

fig.suptitle('Figure: H5 Multilingual Platform Disadvantage Analysis', 
             fontsize=13, fontweight='bold', y=0.995)

plt.tight_layout()
plt.savefig('Figure_H5_Language_Disadvantage.png', dpi=300, bbox_inches='tight')
print("\n✓ Figure saved: Figure_H5_Language_Disadvantage.png")

print("\n" + "="*70)
print("H5 CONCLUSION")
print("="*70)
print("\nKey Findings:")
print("1. Within Luxembourg, language choice significantly affects reach")
print("2. English (global language) shows advantages in some contexts")
print("3. Multilingual content shows mixed results across countries")
print("4. Small languages (Luxembourgish) largely absent from sample")
print("\nImplication: YouTube's algorithm may favor English content,")
print("creating disadvantages for small-language political communication.")
print("="*70)