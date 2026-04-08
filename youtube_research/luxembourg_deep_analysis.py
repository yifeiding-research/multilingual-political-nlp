# ========================================
# 卢森堡深入分析
# 生成与法国、匈牙利相同的详细分析
# ========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, kruskal
from datetime import datetime
import os

# 创建输出文件夹
os.makedirs('outputs/deep_analysis', exist_ok=True)

print("\n" + "="*70)
print("卢森堡深入分析")
print("="*70)

# ==========================================
# 步骤1：加载数据
# ==========================================

print("\n[步骤1] 加载数据...")

df_luxembourg = pd.read_excel('political_influencers_Luxembourg.xlsx')
df_luxembourg['country'] = 'Luxembourg'
df_luxembourg['engagement_rate'] = (df_luxembourg['like_count'] + df_luxembourg['comment_count']) / df_luxembourg['view_count']
df_luxembourg['published_date'] = pd.to_datetime(df_luxembourg['published_date'])
df_luxembourg['year_month'] = df_luxembourg['published_date'].dt.to_period('M')

# 清理数据
df_luxembourg['engagement_rate'] = df_luxembourg['engagement_rate'].replace([np.inf, -np.inf], np.nan)
df_luxembourg = df_luxembourg[df_luxembourg['view_count'] > 0].copy()

print(f"✓ 卢森堡: {len(df_luxembourg)} 个视频, {df_luxembourg['channel_name'].nunique()} 个频道")

# ==========================================
# 步骤2：生成频道汇总
# ==========================================

print("\n[步骤2] 生成频道汇总...")

def get_channel_summary(df, country_name):
    """生成频道汇总"""
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

luxembourg_channels = get_channel_summary(df_luxembourg, 'Luxembourg')

print(f"✓ 频道汇总完成")

# ==========================================
# 步骤3：Top 10频道分析
# ==========================================

print("\n" + "="*70)
print("Top 10频道分析（按互动率）")
print("="*70)

print("\n【卢森堡 Top 10】")
luxembourg_top10 = luxembourg_channels.head(10)
print(luxembourg_top10[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']])

# ==========================================
# 步骤4：生成图表
# ==========================================

print("\n[步骤3] 生成图表...")

sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# 图1: Top 10频道互动率
fig, ax = plt.subplots(figsize=(12, 8))

luxembourg_top10_sorted = luxembourg_top10.sort_values('avg_engagement_rate')
colors_lux = ['#2ca02c'] * len(luxembourg_top10_sorted)

ax.barh(range(len(luxembourg_top10_sorted)), luxembourg_top10_sorted['avg_engagement_rate'].values, 
        color=colors_lux, alpha=0.8)
ax.set_yticks(range(len(luxembourg_top10_sorted)))
ax.set_yticklabels(luxembourg_top10_sorted['channel_name'].values, fontsize=10)
ax.set_xlabel('Average Engagement Rate', fontweight='bold')
ax.set_title('Luxembourg: Top 10 Channels by Engagement Rate', fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3, axis='x')

# 添加数值标签
for i, v in enumerate(luxembourg_top10_sorted['avg_engagement_rate'].values):
    ax.text(v + 0.005, i, f'{v:.4f}', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_01_top10_channels.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_01_top10_channels.png")
plt.close()

# 图2: 时间序列分析
fig, ax = plt.subplots(figsize=(14, 7))

luxembourg_monthly = df_luxembourg.groupby('year_month').agg({
    'engagement_rate': 'mean',
    'view_count': 'mean'
}).reset_index()
luxembourg_monthly = luxembourg_monthly.sort_values('year_month')

ax.plot(range(len(luxembourg_monthly)), luxembourg_monthly['engagement_rate'].values, 
        marker='o', linewidth=2.5, color='#2ca02c', markersize=10, label='Engagement Rate')
ax.fill_between(range(len(luxembourg_monthly)), luxembourg_monthly['engagement_rate'].values, alpha=0.3, color='#2ca02c')

ax.set_ylabel('Average Engagement Rate', fontweight='bold', fontsize=12)
ax.set_xlabel('Month', fontweight='bold', fontsize=12)
ax.set_title('Luxembourg: Engagement Rate Trend (June-December 2025)', fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(luxembourg_monthly)))
ax.set_xticklabels([str(m) for m in luxembourg_monthly['year_month'].values], rotation=45)

# 添加数值标签
for i, v in enumerate(luxembourg_monthly['engagement_rate'].values):
    ax.text(i, v + 0.0005, f'{v:.4f}', ha='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_02_time_series_trend.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_02_time_series_trend.png")
plt.close()

# 图3: 观看量vs互动率
fig, ax = plt.subplots(figsize=(14, 8))

ax.scatter(df_luxembourg['view_count'], df_luxembourg['engagement_rate']*100, 
          alpha=0.6, s=80, color='#2ca02c', edgecolors='darkgreen', linewidth=0.5)
ax.set_xlabel('View Count (log scale)', fontweight='bold', fontsize=12)
ax.set_ylabel('Engagement Rate (%)', fontweight='bold', fontsize=12)
ax.set_xscale('log')
ax.set_title('Luxembourg: View Count vs Engagement Rate', fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3)

# 计算相关性
corr_lux, p_lux = spearmanr(df_luxembourg['view_count'].dropna(), 
                            df_luxembourg['engagement_rate'].dropna())
ax.text(0.05, 0.95, f'Spearman r = {corr_lux:.3f}\np = {p_lux:.4f}', 
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_03_view_engagement_scatter.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_03_view_engagement_scatter.png")
plt.close()

# 图4: 视频产出分布
fig, ax = plt.subplots(figsize=(12, 8))

luxembourg_video_count = df_luxembourg.groupby('channel_name').size().sort_values(ascending=False).head(10)
ax.barh(range(len(luxembourg_video_count)), luxembourg_video_count.values, color='#2ca02c', alpha=0.8)
ax.set_yticks(range(len(luxembourg_video_count)))
ax.set_yticklabels(luxembourg_video_count.index, fontsize=10)
ax.set_xlabel('Number of Videos', fontweight='bold', fontsize=12)
ax.set_title('Luxembourg: Top 10 Channels by Video Count', fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(luxembourg_video_count.values):
    ax.text(v + 2, i, f'{v}', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_04_video_count_distribution.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_04_video_count_distribution.png")
plt.close()

# 图5: 观看量不平等分析
fig, ax = plt.subplots(figsize=(12, 8))

def calculate_gini(values):
    """计算Gini系数"""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    cumsum = np.cumsum(sorted_vals)
    return (2 * np.sum((np.arange(1, n+1)) * sorted_vals)) / (n * np.sum(sorted_vals)) - (n + 1) / n

luxembourg_gini = calculate_gini(df_luxembourg['view_count'].values)

print(f"\nGini系数（观看量不平等指数）:")
print(f"  卢森堡: {luxembourg_gini:.4f}")

luxembourg_top5_views = luxembourg_channels.head(5).sort_values('total_views', ascending=True)

ax.barh(range(len(luxembourg_top5_views)), luxembourg_top5_views['total_views'].values, 
        color='#2ca02c', alpha=0.8, edgecolor='darkgreen', linewidth=1.5)
ax.set_yticks(range(len(luxembourg_top5_views)))
ax.set_yticklabels(luxembourg_top5_views['channel_name'].values, fontsize=10)
ax.set_xlabel('Total Views (log scale)', fontweight='bold', fontsize=12)
ax.set_xscale('log')
ax.set_title(f'Luxembourg: Top 5 Channels by Total Views\n(Gini Coefficient = {luxembourg_gini:.4f})', 
            fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3, axis='x')

for i, v in enumerate(luxembourg_top5_views['total_views'].values):
    ax.text(v * 1.15, i, f'{v:,.0f}', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_05_inequality_analysis.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_05_inequality_analysis.png")
plt.close()

# 图6: 视频数量vs互动率
fig, ax = plt.subplots(figsize=(12, 8))

luxembourg_prod_corr, luxembourg_prod_p = spearmanr(luxembourg_channels['video_count'], 
                                                      luxembourg_channels['avg_engagement_rate'])

print(f"\n视频数量 vs 互动率 相关性:")
print(f"  卢森堡: r = {luxembourg_prod_corr:.4f}, p = {luxembourg_prod_p:.4f}")

ax.scatter(luxembourg_channels['video_count'], luxembourg_channels['avg_engagement_rate']*100, 
          s=150, alpha=0.6, color='#2ca02c', edgecolors='darkgreen', linewidth=1.5)
ax.set_xlabel('Number of Videos', fontweight='bold', fontsize=12)
ax.set_ylabel('Average Engagement Rate (%)', fontweight='bold', fontsize=12)
ax.set_title(f'Luxembourg: Video Count vs Engagement Rate\n(r = {luxembourg_prod_corr:.3f}, p = {luxembourg_prod_p:.4f})', 
            fontweight='bold', fontsize=14)
ax.grid(True, alpha=0.3)

# 添加频道名标签（Top 5）
for idx, row in luxembourg_channels.head(5).iterrows():
    ax.annotate(row['channel_name'][:20], (row['video_count'], row['avg_engagement_rate']*100),
               fontsize=8, alpha=0.8, xytext=(5, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig('outputs/deep_analysis/lux_06_video_count_engagement.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: lux_06_video_count_engagement.png")
plt.close()

# ==========================================
# 步骤5：生成详细报告
# ==========================================

print("\n[步骤4] 生成详细报告...")

report = f"""
DEEP ANALYSIS: LUXEMBOURG
{'='*70}

1. BASIC STATISTICS
{'='*70}

Channels: {df_luxembourg['channel_name'].nunique()}
Total Videos: {len(df_luxembourg):,}
Date Range: {df_luxembourg['published_date'].min().strftime('%B %Y')} to {df_luxembourg['published_date'].max().strftime('%B %Y')}

Engagement Rate:
  Mean: {df_luxembourg['engagement_rate'].mean():.4f}
  Median: {df_luxembourg['engagement_rate'].median():.4f}
  Std Dev: {df_luxembourg['engagement_rate'].std():.4f}
  Min: {df_luxembourg['engagement_rate'].min():.4f}
  Max: {df_luxembourg['engagement_rate'].max():.4f}

View Count:
  Mean: {df_luxembourg['view_count'].mean():,.0f}
  Median: {df_luxembourg['view_count'].median():,.0f}
  Total: {df_luxembourg['view_count'].sum():,.0f}
  Min: {df_luxembourg['view_count'].min():,.0f}
  Max: {df_luxembourg['view_count'].max():,.0f}

Like Count:
  Mean: {df_luxembourg['like_count'].mean():.0f}
  Total: {df_luxembourg['like_count'].sum():,.0f}

Comment Count:
  Mean: {df_luxembourg['comment_count'].mean():.0f}
  Total: {df_luxembourg['comment_count'].sum():,.0f}

2. TOP 5 CHANNELS BY ENGAGEMENT
{'='*70}

{luxembourg_channels.head(5)[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].to_string(index=False)}

3. TOP 5 CHANNELS BY VIDEO PRODUCTION
{'='*70}

{df_luxembourg.groupby('channel_name').size().sort_values(ascending=False).head(5).to_string()}

4. TEMPORAL TRENDS
{'='*70}

Months Analyzed: {df_luxembourg['year_month'].nunique()}

Monthly Engagement Rate:
  Highest: {luxembourg_monthly['engagement_rate'].max():.4f} ({luxembourg_monthly.loc[luxembourg_monthly['engagement_rate'].idxmax(), 'year_month']})
  Lowest: {luxembourg_monthly['engagement_rate'].min():.4f} ({luxembourg_monthly.loc[luxembourg_monthly['engagement_rate'].idxmin(), 'year_month']})
  Trend: {"Declining" if luxembourg_monthly['engagement_rate'].iloc[-1] < luxembourg_monthly['engagement_rate'].iloc[0] else "Rising"}

Month-by-Month Breakdown:
{luxembourg_monthly[['year_month', 'engagement_rate']].to_string(index=False)}

5. VIEW-ENGAGEMENT CORRELATION
{'='*70}

Spearman Rank Correlation:
  r: {corr_lux:.4f}
  p-value: {p_lux:.4f}
  Interpretation: {"SIGNIFICANT positive correlation" if p_lux < 0.05 and corr_lux > 0 else "SIGNIFICANT negative correlation" if p_lux < 0.05 and corr_lux < 0 else "No significant correlation"}

Implication: {"Higher view counts associate with higher engagement" if corr_lux > 0 else "Higher view counts associate with lower engagement"}

6. VIDEO COUNT-ENGAGEMENT CORRELATION
{'='*70}

Spearman Rank Correlation:
  r: {luxembourg_prod_corr:.4f}
  p-value: {luxembourg_prod_p:.4f}
  Interpretation: {"SIGNIFICANT correlation" if luxembourg_prod_p < 0.05 else "No significant correlation"}

Implication: {"Video production volume {'IS' if luxembourg_prod_p < 0.05 else 'is NOT'} significantly related to engagement rates"}

7. INEQUALITY MEASURE (GINI COEFFICIENT)
{'='*70}

Gini Index: {luxembourg_gini:.4f}
Interpretation: {"High inequality - Few channels dominate" if luxembourg_gini > 0.7 else "Moderate inequality" if luxembourg_gini > 0.5 else "Relatively equal distribution"}

Top 5 Channels View Share: {(luxembourg_top5_views['total_views'].sum() / df_luxembourg['view_count'].sum() * 100):.1f}%
Remaining 13 Channels View Share: {(100 - luxembourg_top5_views['total_views'].sum() / df_luxembourg['view_count'].sum() * 100):.1f}%

8. KEY FINDINGS & CHARACTERISTICS
{'='*70}

8.1 Engagement Landscape
   - Highest Engagement Channel: {luxembourg_channels.iloc[0]['channel_name']} ({luxembourg_channels.iloc[0]['avg_engagement_rate']:.4f})
   - Lowest Engagement Channel: {luxembourg_channels.iloc[-1]['channel_name']} ({luxembourg_channels.iloc[-1]['avg_engagement_rate']:.4f})
   - Engagement Variance: {(luxembourg_channels['avg_engagement_rate'].max() - luxembourg_channels['avg_engagement_rate'].min()):.4f}

8.2 Content Production Strategy
   - Most Prolific Channel: {df_luxembourg.groupby('channel_name').size().idxmax()} ({df_luxembourg.groupby('channel_name').size().max()} videos)
   - Single-Video Channels: {(df_luxembourg.groupby('channel_name').size() == 1).sum()}
   - Average Videos per Channel: {len(df_luxembourg) / df_luxembourg['channel_name'].nunique():.1f}

8.3 Audience Scale Distribution
   - Channels with <1K total views: {(luxembourg_channels['total_views'] < 1000).sum()}
   - Channels with 1K-10K views: {((luxembourg_channels['total_views'] >= 1000) & (luxembourg_channels['total_views'] < 10000)).sum()}
   - Channels with 10K-100K views: {((luxembourg_channels['total_views'] >= 10000) & (luxembourg_channels['total_views'] < 100000)).sum()}
   - Channels with >100K views: {(luxembourg_channels['total_views'] >= 100000).sum()}

8.4 Comparison to Other Countries
   - Engagement vs France: {df_luxembourg['engagement_rate'].mean():.4f} vs 0.0382 (Luxembourg is {"HIGHER" if df_luxembourg['engagement_rate'].mean() > 0.0382 else "LOWER"})
   - Engagement vs Hungary: {df_luxembourg['engagement_rate'].mean():.4f} vs 0.0449 (Luxembourg is {"HIGHER" if df_luxembourg['engagement_rate'].mean() > 0.0449 else "LOWER"})
   - Gini Index: {luxembourg_gini:.4f} (between France's 0.7723 and Hungary's 0.6750)

{'='*70}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

print(report)

# 保存报告
with open('outputs/deep_analysis/luxembourg_deep_analysis_report.txt', 'w') as f:
    f.write(report)

print("\n✓ 报告已保存: luxembourg_deep_analysis_report.txt")

# ==========================================
# 步骤6：保存详细数据
# ==========================================

luxembourg_channels.to_csv('outputs/deep_analysis/luxembourg_detailed_channels.csv', index=False)
luxembourg_monthly.to_csv('outputs/deep_analysis/luxembourg_monthly_trends.csv', index=False)

print("✓ 已保存详细频道和月度趋势数据")

print("\n" + "="*70)
print("✅ 卢森堡深入分析完成！")
print("="*70)
print("\n已生成的文件:")
print("  📊 图表 (6个):")
print("     - outputs/deep_analysis/lux_01_top10_channels.png")
print("     - outputs/deep_analysis/lux_02_time_series_trend.png")
print("     - outputs/deep_analysis/lux_03_view_engagement_scatter.png")
print("     - outputs/deep_analysis/lux_04_video_count_distribution.png")
print("     - outputs/deep_analysis/lux_05_inequality_analysis.png")
print("     - outputs/deep_analysis/lux_06_video_count_engagement.png")
print("  📄 报告:")
print("     - outputs/deep_analysis/luxembourg_deep_analysis_report.txt")
print("  📋 数据:")
print("     - outputs/deep_analysis/luxembourg_detailed_channels.csv")
print("     - outputs/deep_analysis/luxembourg_monthly_trends.csv")