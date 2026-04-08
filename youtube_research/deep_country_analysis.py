# ========================================
# 法国和匈牙利深入分析
# 生成与卢森堡相同级别的详细分析
# ========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, kruskal, mannwhitneyu
from datetime import datetime
import os

# 创建输出文件夹
os.makedirs('outputs/deep_analysis', exist_ok=True)

print("\n" + "="*70)
print("法国和匈牙利深入分析")
print("="*70)

# ==========================================
# 步骤1：加载数据
# ==========================================

print("\n[步骤1] 加载数据...")

df_france = pd.read_excel('political_influencers_France.xlsx')
df_france['country'] = 'France'
df_france['engagement_rate'] = (df_france['like_count'] + df_france['comment_count']) / df_france['view_count']
df_france['published_date'] = pd.to_datetime(df_france['published_date'])
df_france['year_month'] = df_france['published_date'].dt.to_period('M')

df_hungary = pd.read_excel('political_influencers_Hungary.xlsx')
df_hungary['country'] = 'Hungary'
df_hungary['engagement_rate'] = (df_hungary['like_count'] + df_hungary['comment_count']) / df_hungary['view_count']
df_hungary['published_date'] = pd.to_datetime(df_hungary['published_date'])
df_hungary['year_month'] = df_hungary['published_date'].dt.to_period('M')

# 清理数据
df_france['engagement_rate'] = df_france['engagement_rate'].replace([np.inf, -np.inf], np.nan)
df_france = df_france[df_france['view_count'] > 0].copy()

df_hungary['engagement_rate'] = df_hungary['engagement_rate'].replace([np.inf, -np.inf], np.nan)
df_hungary = df_hungary[df_hungary['view_count'] > 0].copy()

print(f"✓ 法国: {len(df_france)} 个视频, {df_france['channel_name'].nunique()} 个频道")
print(f"✓ 匈牙利: {len(df_hungary)} 个视频, {df_hungary['channel_name'].nunique()} 个频道")

# ==========================================
# 步骤2：生成频道汇总
# ==========================================

print("\n[步骤2] 生成频道汇总...")

def get_channel_summary(df, country_name):
    """为一个国家生成频道汇总"""
    summary_data = []
    
    for channel in df['channel_name'].unique():
        channel_data = df[df['channel_name'] == channel]
        summary_data.append({
            'channel_name': channel,
            'total_views': channel_data['view_count'].sum(),
            'avg_views': channel_data['view_count'].mean(),
            'video_count': len(channel_data),
            'total_likes': channel_data['like_count'].sum(),
            'avg_likes': channel_data['like_count'].mean(),
            'total_comments': channel_data['comment_count'].sum(),
            'avg_comments': channel_data['comment_count'].mean(),
            'avg_engagement_rate': channel_data['engagement_rate'].mean(),
            'country': country_name
        })
    
    return pd.DataFrame(summary_data).sort_values('avg_engagement_rate', ascending=False)

france_channels = get_channel_summary(df_france, 'France')
hungary_channels = get_channel_summary(df_hungary, 'Hungary')

print(f"✓ 频道汇总完成")

# ==========================================
# 步骤3：Top 10频道分析
# ==========================================

print("\n" + "="*70)
print("Top 10频道分析（按互动率）")
print("="*70)

print("\n【法国 Top 10】")
france_top10 = france_channels.head(10)
print(france_top10[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']])

print("\n【匈牙利 Top 10】")
hungary_top10 = hungary_channels.head(10)
print(hungary_top10[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']])

# ==========================================
# 步骤4：生成Top 10频道对比图
# ==========================================

print("\n[步骤3] 生成图表...")

sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# 图1: 两国Top 10频道互动率对比
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# 法国
ax1 = axes[0]
france_top10_sorted = france_top10.sort_values('avg_engagement_rate')
ax1.barh(range(len(france_top10_sorted)), france_top10_sorted['avg_engagement_rate'].values, color='#1f77b4', alpha=0.8)
ax1.set_yticks(range(len(france_top10_sorted)))
ax1.set_yticklabels(france_top10_sorted['channel_name'].values, fontsize=9)
ax1.set_xlabel('Average Engagement Rate', fontweight='bold')
ax1.set_title('France: Top 10 Channels by Engagement Rate', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')

# 添加数值标签
for i, v in enumerate(france_top10_sorted['avg_engagement_rate'].values):
    ax1.text(v + 0.0005, i, f'{v:.4f}', va='center', fontweight='bold', fontsize=9)

# 匈牙利
ax2 = axes[1]
hungary_top10_sorted = hungary_top10.sort_values('avg_engagement_rate')
ax2.barh(range(len(hungary_top10_sorted)), hungary_top10_sorted['avg_engagement_rate'].values, color='#ff7f0e', alpha=0.8)
ax2.set_yticks(range(len(hungary_top10_sorted)))
ax2.set_yticklabels(hungary_top10_sorted['channel_name'].values, fontsize=9)
ax2.set_xlabel('Average Engagement Rate', fontweight='bold')
ax2.set_title('Hungary: Top 10 Channels by Engagement Rate', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

# 添加数值标签
for i, v in enumerate(hungary_top10_sorted['avg_engagement_rate'].values):
    ax2.text(v + 0.0005, i, f'{v:.4f}', va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/01_top10_channels_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 01_top10_channels_comparison.png")
plt.close()

# ==========================================
# 步骤5：时间序列分析
# ==========================================

print("\n[步骤4] 时间序列分析...")

fig, axes = plt.subplots(2, 1, figsize=(14, 10))

# 法国时间序列
france_monthly = df_france.groupby('year_month').agg({
    'engagement_rate': 'mean',
    'view_count': 'mean'
}).reset_index()
france_monthly = france_monthly.sort_values('year_month')

ax1 = axes[0]
ax1.plot(range(len(france_monthly)), france_monthly['engagement_rate'].values, 
        marker='o', linewidth=2.5, color='#1f77b4', markersize=8)
ax1.set_ylabel('Average Engagement Rate', fontweight='bold')
ax1.set_title('France: Engagement Rate Trend (June-December 2025)', fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_xticks(range(len(france_monthly)))
ax1.set_xticklabels([str(m) for m in france_monthly['year_month'].values], rotation=45)

# 匈牙利时间序列
hungary_monthly = df_hungary.groupby('year_month').agg({
    'engagement_rate': 'mean',
    'view_count': 'mean'
}).reset_index()
hungary_monthly = hungary_monthly.sort_values('year_month')

ax2 = axes[1]
ax2.plot(range(len(hungary_monthly)), hungary_monthly['engagement_rate'].values, 
        marker='o', linewidth=2.5, color='#ff7f0e', markersize=8)
ax2.set_ylabel('Average Engagement Rate', fontweight='bold')
ax2.set_xlabel('Month', fontweight='bold')
ax2.set_title('Hungary: Engagement Rate Trend (June-December 2025)', fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(len(hungary_monthly)))
ax2.set_xticklabels([str(m) for m in hungary_monthly['year_month'].values], rotation=45)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/02_time_series_trends.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 02_time_series_trends.png")
plt.close()

# ==========================================
# 步骤6：观看量vs互动率分析
# ==========================================

print("\n[步骤5] 观看量vs互动率分析...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# 法国
ax1 = axes[0]
ax1.scatter(df_france['view_count'], df_france['engagement_rate']*100, 
           alpha=0.5, s=50, color='#1f77b4')
ax1.set_xlabel('View Count (log scale)', fontweight='bold')
ax1.set_ylabel('Engagement Rate (%)', fontweight='bold')
ax1.set_xscale('log')
ax1.set_title('France: View Count vs Engagement Rate', fontweight='bold')
ax1.grid(True, alpha=0.3)

# 计算相关性
corr_fr, p_fr = spearmanr(df_france['view_count'].dropna(), 
                          df_france['engagement_rate'].dropna())
ax1.text(0.05, 0.95, f'Spearman r = {corr_fr:.3f}\np = {p_fr:.4f}', 
        transform=ax1.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# 匈牙利
ax2 = axes[1]
ax2.scatter(df_hungary['view_count'], df_hungary['engagement_rate']*100, 
           alpha=0.5, s=50, color='#ff7f0e')
ax2.set_xlabel('View Count (log scale)', fontweight='bold')
ax2.set_ylabel('Engagement Rate (%)', fontweight='bold')
ax2.set_xscale('log')
ax2.set_title('Hungary: View Count vs Engagement Rate', fontweight='bold')
ax2.grid(True, alpha=0.3)

# 计算相关性
corr_hu, p_hu = spearmanr(df_hungary['view_count'].dropna(), 
                          df_hungary['engagement_rate'].dropna())
ax2.text(0.05, 0.95, f'Spearman r = {corr_hu:.3f}\np = {p_hu:.4f}', 
        transform=ax2.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('outputs/deep_analysis/03_view_engagement_scatter.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 03_view_engagement_scatter.png")
plt.close()

# ==========================================
# 步骤7：视频产出分布
# ==========================================

print("\n[步骤6] 视频产出分布...")

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# 法国Top 10最多产频道
france_video_count = df_france.groupby('channel_name').size().sort_values(ascending=False).head(10)
ax1 = axes[0]
ax1.barh(range(len(france_video_count)), france_video_count.values, color='#1f77b4', alpha=0.8)
ax1.set_yticks(range(len(france_video_count)))
ax1.set_yticklabels(france_video_count.index, fontsize=9)
ax1.set_xlabel('Number of Videos', fontweight='bold')
ax1.set_title('France: Top 10 Channels by Video Count', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(france_video_count.values):
    ax1.text(v + 2, i, f'{v}', va='center', fontweight='bold')

# 匈牙利Top 10最多产频道
hungary_video_count = df_hungary.groupby('channel_name').size().sort_values(ascending=False).head(10)
ax2 = axes[1]
ax2.barh(range(len(hungary_video_count)), hungary_video_count.values, color='#ff7f0e', alpha=0.8)
ax2.set_yticks(range(len(hungary_video_count)))
ax2.set_yticklabels(hungary_video_count.index, fontsize=9)
ax2.set_xlabel('Number of Videos', fontweight='bold')
ax2.set_title('Hungary: Top 10 Channels by Video Count', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(hungary_video_count.values):
    ax2.text(v + 2, i, f'{v}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('outputs/deep_analysis/04_video_count_distribution.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 04_video_count_distribution.png")
plt.close()

# ==========================================
# 步骤8：观看量不平等分析（Gini系数）
# ==========================================

print("\n[步骤7] 不平等分析...")

def calculate_gini(values):
    """计算Gini系数"""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    cumsum = np.cumsum(sorted_vals)
    return (2 * np.sum((np.arange(1, n+1)) * sorted_vals)) / (n * np.sum(sorted_vals)) - (n + 1) / n

france_gini = calculate_gini(df_france['view_count'].values)
hungary_gini = calculate_gini(df_hungary['view_count'].values)

print(f"\nGini系数（观看量不平等指数）:")
print(f"  法国: {france_gini:.4f}")
print(f"  匈牙利: {hungary_gini:.4f}")

# 图：Top频道总观看数对比
france_top5_views = france_channels.head(5).sort_values('total_views', ascending=True)
hungary_top5_views = hungary_channels.head(5).sort_values('total_views', ascending=True)

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

ax1 = axes[0]
ax1.barh(range(len(france_top5_views)), france_top5_views['total_views'].values, color='#1f77b4', alpha=0.8)
ax1.set_yticks(range(len(france_top5_views)))
ax1.set_yticklabels(france_top5_views['channel_name'].values, fontsize=9)
ax1.set_xlabel('Total Views (log scale)', fontweight='bold')
ax1.set_xscale('log')
ax1.set_title(f'France: Top 5 Channels by Total Views\n(Gini = {france_gini:.4f})', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(france_top5_views['total_views'].values):
    ax1.text(v * 1.1, i, f'{v:,.0f}', va='center', fontweight='bold', fontsize=9)

ax2 = axes[1]
ax2.barh(range(len(hungary_top5_views)), hungary_top5_views['total_views'].values, color='#ff7f0e', alpha=0.8)
ax2.set_yticks(range(len(hungary_top5_views)))
ax2.set_yticklabels(hungary_top5_views['channel_name'].values, fontsize=9)
ax2.set_xlabel('Total Views (log scale)', fontweight='bold')
ax2.set_xscale('log')
ax2.set_title(f'Hungary: Top 5 Channels by Total Views\n(Gini = {hungary_gini:.4f})', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(hungary_top5_views['total_views'].values):
    ax2.text(v * 1.1, i, f'{v:,.0f}', va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/05_inequality_analysis.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 05_inequality_analysis.png")
plt.close()

# ==========================================
# 步骤9：视频数量vs互动率关系
# ==========================================

print("\n[步骤8] 视频数量vs互动率关系...")

france_prod_corr, france_prod_p = spearmanr(france_channels['video_count'], 
                                            france_channels['avg_engagement_rate'])
hungary_prod_corr, hungary_prod_p = spearmanr(hungary_channels['video_count'], 
                                              hungary_channels['avg_engagement_rate'])

print(f"\n视频数量 vs 互动率 相关性:")
print(f"  法国: r = {france_prod_corr:.4f}, p = {france_prod_p:.4f}")
print(f"  匈牙利: r = {hungary_prod_corr:.4f}, p = {hungary_prod_p:.4f}")

# 图表
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

ax1 = axes[0]
ax1.scatter(france_channels['video_count'], france_channels['avg_engagement_rate']*100, 
           s=100, alpha=0.6, color='#1f77b4')
ax1.set_xlabel('Number of Videos', fontweight='bold')
ax1.set_ylabel('Average Engagement Rate (%)', fontweight='bold')
ax1.set_title(f'France: Video Count vs Engagement Rate\n(r = {france_prod_corr:.3f}, p = {france_prod_p:.4f})', 
             fontweight='bold')
ax1.grid(True, alpha=0.3)

# 添加频道名标签（Top 5）
for idx, row in france_channels.head(5).iterrows():
    ax1.annotate(row['channel_name'], (row['video_count'], row['avg_engagement_rate']*100),
                fontsize=7, alpha=0.7)

ax2 = axes[1]
ax2.scatter(hungary_channels['video_count'], hungary_channels['avg_engagement_rate']*100, 
           s=100, alpha=0.6, color='#ff7f0e')
ax2.set_xlabel('Number of Videos', fontweight='bold')
ax2.set_ylabel('Average Engagement Rate (%)', fontweight='bold')
ax2.set_title(f'Hungary: Video Count vs Engagement Rate\n(r = {hungary_prod_corr:.3f}, p = {hungary_prod_p:.4f})', 
             fontweight='bold')
ax2.grid(True, alpha=0.3)

# 添加频道名标签（Top 5）
for idx, row in hungary_channels.head(5).iterrows():
    ax2.annotate(row['channel_name'], (row['video_count'], row['avg_engagement_rate']*100),
                fontsize=7, alpha=0.7)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/06_video_count_engagement.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 06_video_count_engagement.png")
plt.close()

# ==========================================
# 步骤10：生成详细报告
# ==========================================

print("\n[步骤9] 生成详细报告...")

report = f"""
DEEP ANALYSIS: FRANCE AND HUNGARY
{'='*70}

1. FRANCE ANALYSIS
{'='*70}

1.1 Basic Statistics
--------------------
Channels: {df_france['channel_name'].nunique()}
Total Videos: {len(df_france):,}
Date Range: {df_france['published_date'].min().strftime('%B %Y')} to {df_france['published_date'].max().strftime('%B %Y')}

Engagement Rate:
  Mean: {df_france['engagement_rate'].mean():.4f}
  Median: {df_france['engagement_rate'].median():.4f}
  Std Dev: {df_france['engagement_rate'].std():.4f}

View Count:
  Mean: {df_france['view_count'].mean():,.0f}
  Median: {df_france['view_count'].median():,.0f}
  Total: {df_france['view_count'].sum():,.0f}

1.2 Top 5 Channels by Engagement
---------------------------------
{france_channels.head(5)[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].to_string(index=False)}

1.3 Top 5 Channels by Video Production
---------------------------------------
{df_france.groupby('channel_name').size().sort_values(ascending=False).head(5).to_string()}

1.4 Temporal Trends
--------------------
Months Analyzed: {df_france['year_month'].nunique()}
Engagement Rate Trend:
  Highest: {france_monthly['engagement_rate'].max():.4f} ({france_monthly.loc[france_monthly['engagement_rate'].idxmax(), 'year_month']})
  Lowest: {france_monthly['engagement_rate'].min():.4f} ({france_monthly.loc[france_monthly['engagement_rate'].idxmin(), 'year_month']})

1.5 View-Engagement Correlation
---------------------------------
Spearman r: {corr_fr:.4f}
P-value: {p_fr:.4f}
Interpretation: {"SIGNIFICANT positive correlation" if p_fr < 0.05 else "No significant correlation"}

1.6 Video Count-Engagement Correlation
---------------------------------------
Spearman r: {france_prod_corr:.4f}
P-value: {france_prod_p:.4f}
Interpretation: {"SIGNIFICANT correlation" if france_prod_p < 0.05 else "No significant correlation"}

1.7 Inequality Measure (Gini Coefficient)
------------------------------------------
Gini Index: {france_gini:.4f}
Interpretation: {"High inequality - Few channels dominate" if france_gini > 0.7 else "Moderate inequality" if france_gini > 0.5 else "Relatively equal distribution"}

{'='*70}

2. HUNGARY ANALYSIS
{'='*70}

2.1 Basic Statistics
--------------------
Channels: {df_hungary['channel_name'].nunique()}
Total Videos: {len(df_hungary):,}
Date Range: {df_hungary['published_date'].min().strftime('%B %Y')} to {df_hungary['published_date'].max().strftime('%B %Y')}

Engagement Rate:
  Mean: {df_hungary['engagement_rate'].mean():.4f}
  Median: {df_hungary['engagement_rate'].median():.4f}
  Std Dev: {df_hungary['engagement_rate'].std():.4f}

View Count:
  Mean: {df_hungary['view_count'].mean():,.0f}
  Median: {df_hungary['view_count'].median():,.0f}
  Total: {df_hungary['view_count'].sum():,.0f}

2.2 Top 5 Channels by Engagement
---------------------------------
{hungary_channels.head(5)[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].to_string(index=False)}

2.3 Top 5 Channels by Video Production
---------------------------------------
{df_hungary.groupby('channel_name').size().sort_values(ascending=False).head(5).to_string()}

2.4 Temporal Trends
--------------------
Months Analyzed: {df_hungary['year_month'].nunique()}
Engagement Rate Trend:
  Highest: {hungary_monthly['engagement_rate'].max():.4f} ({hungary_monthly.loc[hungary_monthly['engagement_rate'].idxmax(), 'year_month']})
  Lowest: {hungary_monthly['engagement_rate'].min():.4f} ({hungary_monthly.loc[hungary_monthly['engagement_rate'].idxmin(), 'year_month']})

2.5 View-Engagement Correlation
---------------------------------
Spearman r: {corr_hu:.4f}
P-value: {p_hu:.4f}
Interpretation: {"SIGNIFICANT positive correlation" if p_hu < 0.05 else "No significant correlation"}

2.6 Video Count-Engagement Correlation
---------------------------------------
Spearman r: {hungary_prod_corr:.4f}
P-value: {hungary_prod_p:.4f}
Interpretation: {"SIGNIFICANT correlation" if hungary_prod_p < 0.05 else "No significant correlation"}

2.7 Inequality Measure (Gini Coefficient)
------------------------------------------
Gini Index: {hungary_gini:.4f}
Interpretation: {"High inequality - Few channels dominate" if hungary_gini > 0.7 else "Moderate inequality" if hungary_gini > 0.5 else "Relatively equal distribution"}

{'='*70}

3. COMPARATIVE INSIGHTS
{'='*70}

Engagement Rate:
  Winner: {"Hungary" if df_hungary['engagement_rate'].mean() > df_france['engagement_rate'].mean() else "France"}
  Difference: {abs(df_hungary['engagement_rate'].mean() - df_france['engagement_rate'].mean()):.4f}

Reach (Avg Views):
  Winner: {"France" if df_france['view_count'].mean() > df_hungary['view_count'].mean() else "Hungary"}
  Ratio: {max(df_france['view_count'].mean(), df_hungary['view_count'].mean()) / min(df_france['view_count'].mean(), df_hungary['view_count'].mean()):.2f}x

Video Production:
  Winner: {"Hungary" if len(df_hungary) > len(df_france) else "France"}
  Total Videos Difference: {abs(len(df_hungary) - len(df_france))}

Inequality:
  More Equal: {"Hungary" if hungary_gini < france_gini else "France"}
  Gini Difference: {abs(hungary_gini - france_gini):.4f}

{'='*70}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

print(report)

# 保存报告
with open('outputs/deep_analysis/deep_analysis_report.txt', 'w') as f:
    f.write(report)

print("\n✓ 报告已保存: deep_analysis_report.txt")

# ==========================================
# 步骤11：保存Top频道详细数据
# ==========================================

france_channels.head(20).to_csv('outputs/deep_analysis/france_detailed_channels.csv', index=False)
hungary_channels.head(20).to_csv('outputs/deep_analysis/hungary_detailed_channels.csv', index=False)

print("✓ 已保存详细频道数据")

print("\n" + "="*70)
print("✅ 深入分析完成！")
print("="*70)
print("\n已生成的文件:")
print("  📊 图表 (6个):")
print("     - outputs/deep_analysis/01_top10_channels_comparison.png")
print("     - outputs/deep_analysis/02_time_series_trends.png")
print("     - outputs/deep_analysis/03_view_engagement_scatter.png")
print("     - outputs/deep_analysis/04_video_count_distribution.png")
print("     - outputs/deep_analysis/05_inequality_analysis.png")
print("     - outputs/deep_analysis/06_video_count_engagement.png")
print("  📄 报告:")
print("     - outputs/deep_analysis/deep_analysis_report.txt")
print("  📋 数据:")
print("     - outputs/deep_analysis/france_detailed_channels.csv")
print("     - outputs/deep_analysis/hungary_detailed_channels.csv")