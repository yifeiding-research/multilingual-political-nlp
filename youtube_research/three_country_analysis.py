# ========================================
# 三国政治影响者完整分析脚本
# 为法国、匈牙利、卢森堡生成对比分析
# ========================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, kruskal, mannwhitneyu, f_oneway
from datetime import datetime
import os

# 创建输出文件夹
os.makedirs('outputs/three_country', exist_ok=True)

print("\n" + "="*70)
print("三国政治影响者完整分析")
print("="*70)

# ==========================================
# 步骤1：加载三国数据
# ==========================================

print("\n[步骤1] 加载三国数据...")

try:
    df_france = pd.read_excel('political_influencers_France.xlsx')
    df_france['country'] = 'France'
    # 先计算参与率
    df_france['engagement_rate'] = (df_france['like_count'] + df_france['comment_count']) / df_france['view_count']
    
    df_hungary = pd.read_excel('political_influencers_Hungary.xlsx')
    df_hungary['country'] = 'Hungary'
    df_hungary['engagement_rate'] = (df_hungary['like_count'] + df_hungary['comment_count']) / df_hungary['view_count']
    
    df_luxembourg = pd.read_excel('political_influencers_Luxembourg.xlsx')
    df_luxembourg['country'] = 'Luxembourg'
    df_luxembourg['engagement_rate'] = (df_luxembourg['like_count'] + df_luxembourg['comment_count']) / df_luxembourg['view_count']
    
    # 合并所有数据
    df_all = pd.concat([df_france, df_hungary, df_luxembourg], ignore_index=True)
    
    # 转换日期
    df_all['published_date'] = pd.to_datetime(df_all['published_date'])
    df_all['year_month'] = df_all['published_date'].dt.to_period('M')
    
    print(f"✓ 法国: {len(df_france)} 个视频")
    print(f"✓ 匈牙利: {len(df_hungary)} 个视频")
    print(f"✓ 卢森堡: {len(df_luxembourg)} 个视频")
    print(f"✓ 总计: {len(df_all)} 个视频")
    
except FileNotFoundError as e:
    print(f"❌ 找不到数据文件: {e}")
    exit(1)

# ==========================================
# 步骤2：数据清理
# ==========================================

print("\n[步骤2] 数据清理...")

# 处理无效的参与率
df_all['engagement_rate'] = df_all['engagement_rate'].replace([np.inf, -np.inf], np.nan)

# 删除view_count=0的行
df_all = df_all[df_all['view_count'] > 0].copy()

print(f"✓ 清理完成，有效数据: {len(df_all)} 条")

# ==========================================
# 步骤3：按国家生成频道汇总
# ==========================================

print("\n[步骤3] 生成频道级汇总...")

def generate_channel_summary(df, country_name):
    """为一个国家生成频道汇总"""
    # 先计算频道级的统计
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
            'avg_engagement_rate': channel_data['engagement_rate'].mean()
        })
    
    summary = pd.DataFrame(summary_data)
    summary['country'] = country_name
    
    return summary.sort_values('avg_engagement_rate', ascending=False)

france_summary = generate_channel_summary(df_france, 'France')
hungary_summary = generate_channel_summary(df_hungary, 'Hungary')
luxembourg_summary = generate_channel_summary(df_luxembourg, 'Luxembourg')

print(f"✓ 法国: {len(france_summary)} 个频道")
print(f"✓ 匈牙利: {len(hungary_summary)} 个频道")
print(f"✓ 卢森堡: {len(luxembourg_summary)} 个频道")

# ==========================================
# 步骤4：生成三国对比报告
# ==========================================

print("\n" + "="*70)
print("三国对比分析")
print("="*70)

# 4.1 基本统计
print("\n【基本统计对比】")
print("\n各国平均指标:")
for country in ['France', 'Hungary', 'Luxembourg']:
    country_data = df_all[df_all['country'] == country]
    print(f"\n{country}:")
    print(f"  频道数: {country_data['channel_name'].nunique()}")
    print(f"  视频总数: {len(country_data)}")
    print(f"  平均参与率: {country_data['engagement_rate'].mean():.4f}")
    print(f"  中位数参与率: {country_data['engagement_rate'].median():.4f}")
    print(f"  平均观看数: {country_data['view_count'].mean():,.0f}")
    print(f"  中位数观看数: {country_data['view_count'].median():,.0f}")

# 4.2 Top 10频道对比
print("\n【Top 10频道（按互动率）】")
print("\n法国 Top 5:")
print(france_summary[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].head())
print("\n匈牙利 Top 5:")
print(hungary_summary[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].head())
print("\n卢森堡 Top 5:")
print(luxembourg_summary[['channel_name', 'avg_engagement_rate', 'video_count', 'total_views']].head())

# ==========================================
# 步骤5：统计显著性测试
# ==========================================

print("\n" + "="*70)
print("统计显著性测试")
print("="*70)

# Kruskal-Wallis 测试（三国参与率差异）
france_eng = df_france['engagement_rate'].dropna()
hungary_eng = df_hungary['engagement_rate'].dropna()
luxembourg_eng = df_luxembourg['engagement_rate'].dropna()

h_stat, p_val = kruskal(france_eng, hungary_eng, luxembourg_eng)
print(f"\nKruskal-Wallis Test (参与率):")
print(f"  H = {h_stat:.4f}, p = {p_val:.4f}")
if p_val < 0.05:
    print(f"  ✓ 三国参与率存在显著差异 (p < 0.05)")
else:
    print(f"  × 三国参与率无显著差异 (p >= 0.05)")

# Mann-Whitney U 测试（两两比较）
print(f"\nMann-Whitney U Tests (两两比较):")

fr_hu_u, fr_hu_p = mannwhitneyu(france_eng, hungary_eng)
print(f"  France vs Hungary: U = {fr_hu_u:.0f}, p = {fr_hu_p:.4f}")

fr_lu_u, fr_lu_p = mannwhitneyu(france_eng, luxembourg_eng)
print(f"  France vs Luxembourg: U = {fr_lu_u:.0f}, p = {fr_lu_p:.4f}")

hu_lu_u, hu_lu_p = mannwhitneyu(hungary_eng, luxembourg_eng)
print(f"  Hungary vs Luxembourg: U = {hu_lu_u:.0f}, p = {hu_lu_p:.4f}")

# ==========================================
# 步骤6：生成可视化图表
# ==========================================

print("\n[步骤6] 生成可视化图表...")

# 设置风格
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']

# 图1: 三国参与率对比
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# 1.1 平均参与率对比
ax1 = axes[0, 0]
countries = ['France', 'Hungary', 'Luxembourg']
engagement_means = [df_france['engagement_rate'].mean(), 
                    df_hungary['engagement_rate'].mean(),
                    df_luxembourg['engagement_rate'].mean()]
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

ax1.bar(countries, engagement_means, color=colors, alpha=0.8)
ax1.set_ylabel('Average Engagement Rate', fontweight='bold')
ax1.set_title('Three-Country Comparison: Average Engagement Rate', fontweight='bold')
for i, v in enumerate(engagement_means):
    ax1.text(i, v + 0.0001, f'{v:.4f}', ha='center', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# 1.2 视频数量对比
ax2 = axes[0, 1]
video_counts = [len(df_france), len(df_hungary), len(df_luxembourg)]
ax2.bar(countries, video_counts, color=colors, alpha=0.8)
ax2.set_ylabel('Number of Videos', fontweight='bold')
ax2.set_title('Video Production Volume', fontweight='bold')
for i, v in enumerate(video_counts):
    ax2.text(i, v + 50, f'{v:,}', ha='center', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 1.3 平均观看数对比
ax3 = axes[1, 0]
avg_views = [df_france['view_count'].mean(),
             df_hungary['view_count'].mean(),
             df_luxembourg['view_count'].mean()]
ax3.bar(countries, avg_views, color=colors, alpha=0.8)
ax3.set_ylabel('Average Views per Video', fontweight='bold')
ax3.set_title('Average Reach (Views per Video)', fontweight='bold')
for i, v in enumerate(avg_views):
    ax3.text(i, v + 1000, f'{v:,.0f}', ha='center', fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')

# 1.4 频道数对比
ax4 = axes[1, 1]
channel_counts = [df_france['channel_name'].nunique(),
                  df_hungary['channel_name'].nunique(),
                  df_luxembourg['channel_name'].nunique()]
ax4.bar(countries, channel_counts, color=colors, alpha=0.8)
ax4.set_ylabel('Number of Channels', fontweight='bold')
ax4.set_title('Channel Count by Country', fontweight='bold')
for i, v in enumerate(channel_counts):
    ax4.text(i, v + 0.3, f'{v}', ha='center', fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('outputs/three_country/01_three_country_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 01_three_country_comparison.png")
plt.close()

# 图2: 箱线图（显示分布）
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# 参与率分布
ax1 = axes[0]
engagement_data = [france_eng, hungary_eng, luxembourg_eng]
bp1 = ax1.boxplot(engagement_data, labels=countries, patch_artist=True)
for patch, color in zip(bp1['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax1.set_ylabel('Engagement Rate', fontweight='bold')
ax1.set_title('Engagement Rate Distribution by Country', fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# 观看数分布（对数刻度）
ax2 = axes[1]
view_data = [df_france['view_count'], df_hungary['view_count'], df_luxembourg['view_count']]
bp2 = ax2.boxplot(view_data, labels=countries, patch_artist=True)
for patch, color in zip(bp2['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.set_ylabel('View Count (log scale)', fontweight='bold')
ax2.set_yscale('log')
ax2.set_title('View Count Distribution by Country (Log Scale)', fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('outputs/three_country/02_distribution_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 02_distribution_comparison.png")
plt.close()

# 图3: 时间序列对比
fig, ax = plt.subplots(figsize=(14, 7))

for country, color in zip(['France', 'Hungary', 'Luxembourg'], colors):
    country_data = df_all[df_all['country'] == country].copy()
    monthly = country_data.groupby('year_month')['engagement_rate'].mean().reset_index()
    monthly = monthly.sort_values('year_month')
    
    ax.plot(range(len(monthly)), monthly['engagement_rate'].values, 
           marker='o', linewidth=2.5, label=country, color=color, markersize=8)

ax.set_xlabel('Month', fontweight='bold')
ax.set_ylabel('Average Engagement Rate', fontweight='bold')
ax.set_title('Time Series: Engagement Rate Trends (All Countries)', fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/three_country/03_time_series_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 03_time_series_comparison.png")
plt.close()

# 图4: 观看量vs互动率（三国合并）
fig, ax = plt.subplots(figsize=(14, 8))

color_map = {'France': '#1f77b4', 'Hungary': '#ff7f0e', 'Luxembourg': '#2ca02c'}

for country in ['France', 'Hungary', 'Luxembourg']:
    country_data = df_all[df_all['country'] == country]
    ax.scatter(country_data['view_count'], country_data['engagement_rate']*100,
              label=country, alpha=0.5, s=50, color=color_map[country])

ax.set_xlabel('View Count (log scale)', fontweight='bold')
ax.set_ylabel('Engagement Rate (%)', fontweight='bold')
ax.set_xscale('log')
ax.set_title('View Count vs Engagement Rate (Three Countries)', fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/three_country/04_view_engagement_comparison.png', dpi=300, bbox_inches='tight')
print("✓ 已保存: 04_view_engagement_comparison.png")
plt.close()

# ==========================================
# 步骤7：生成详细报告
# ==========================================

print("\n[步骤7] 生成详细报告...")

report = f"""
THREE-COUNTRY POLITICAL INFLUENCER ANALYSIS REPORT
{'='*70}

1. EXECUTIVE SUMMARY
{'='*70}

This report presents a comparative analysis of political YouTube influencers
across three European nations: France, Hungary, and Luxembourg. The analysis
examines engagement patterns, content production, and reach metrics across
{len(df_all):,} videos from {df_all['channel_name'].nunique()} distinct channels
over the period {df_all['published_date'].min().strftime('%B %Y')} to 
{df_all['published_date'].max().strftime('%B %Y')}.

2. DESCRIPTIVE STATISTICS BY COUNTRY
{'='*70}

FRANCE
------
Channels: {df_france['channel_name'].nunique()}
Videos: {len(df_france):,}
Average Engagement Rate: {df_france['engagement_rate'].mean():.4f}
Median Engagement Rate: {df_france['engagement_rate'].median():.4f}
Average Views per Video: {df_france['view_count'].mean():,.0f}
Median Views per Video: {df_france['view_count'].median():,.0f}
Total Views: {df_france['view_count'].sum():,.0f}

HUNGARY
-------
Channels: {df_hungary['channel_name'].nunique()}
Videos: {len(df_hungary):,}
Average Engagement Rate: {df_hungary['engagement_rate'].mean():.4f}
Median Engagement Rate: {df_hungary['engagement_rate'].median():.4f}
Average Views per Video: {df_hungary['view_count'].mean():,.0f}
Median Views per Video: {df_hungary['view_count'].median():,.0f}
Total Views: {df_hungary['view_count'].sum():,.0f}

LUXEMBOURG
----------
Channels: {df_luxembourg['channel_name'].nunique()}
Videos: {len(df_luxembourg):,}
Average Engagement Rate: {df_luxembourg['engagement_rate'].mean():.4f}
Median Engagement Rate: {df_luxembourg['engagement_rate'].median():.4f}
Average Views per Video: {df_luxembourg['view_count'].mean():,.0f}
Median Views per Video: {df_luxembourg['view_count'].median():,.0f}
Total Views: {df_luxembourg['view_count'].sum():,.0f}

3. STATISTICAL SIGNIFICANCE TESTS
{'='*70}

Kruskal-Wallis H Test (Across Three Countries):
H = {h_stat:.4f}, p = {p_val:.4f}
Result: {"SIGNIFICANT" if p_val < 0.05 else "NOT SIGNIFICANT"} difference

Mann-Whitney U Tests (Pairwise Comparisons):
France vs Hungary: p = {fr_hu_p:.4f} {"SIGNIFICANT" if fr_hu_p < 0.05 else "not significant"}
France vs Luxembourg: p = {fr_lu_p:.4f} {"SIGNIFICANT" if fr_lu_p < 0.05 else "not significant"}
Hungary vs Luxembourg: p = {hu_lu_p:.4f} {"SIGNIFICANT" if hu_lu_p < 0.05 else "not significant"}

4. KEY FINDINGS
{'='*70}

1. Engagement Rate Ranking:
   - Highest: {max([("France", df_france['engagement_rate'].mean()), ("Hungary", df_hungary['engagement_rate'].mean()), ("Luxembourg", df_luxembourg['engagement_rate'].mean())], key=lambda x: x[1])[0]}
   - Lowest: {min([("France", df_france['engagement_rate'].mean()), ("Hungary", df_hungary['engagement_rate'].mean()), ("Luxembourg", df_luxembourg['engagement_rate'].mean())], key=lambda x: x[1])[0]}

2. Production Volume:
   - Most videos: {"France" if len(df_france) > len(df_hungary) and len(df_france) > len(df_luxembourg) else "Hungary" if len(df_hungary) > len(df_luxembourg) else "Luxembourg"}
   - Least videos: {"Luxembourg" if len(df_luxembourg) < len(df_hungary) and len(df_luxembourg) < len(df_france) else "Hungary" if len(df_hungary) < len(df_france) else "France"}

3. Reach (Average Views):
   - Highest: {max([("France", df_france['view_count'].mean()), ("Hungary", df_hungary['view_count'].mean()), ("Luxembourg", df_luxembourg['view_count'].mean())], key=lambda x: x[1])[0]}
   - Lowest: {min([("France", df_france['view_count'].mean()), ("Hungary", df_hungary['view_count'].mean()), ("Luxembourg", df_luxembourg['view_count'].mean())], key=lambda x: x[1])[0]}

5. RECOMMENDATIONS
{'='*70}

1. Further investigate factors driving engagement rate differences
2. Conduct qualitative interviews with top channels
3. Analyze content characteristics (length, topics, production quality)
4. Examine temporal patterns and political event correlations
5. Assess platform algorithm influences on visibility

{'='*70}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

print(report)

# 保存报告
with open('outputs/three_country/three_country_analysis_report.txt', 'w') as f:
    f.write(report)

print("\n✓ 报告已保存: three_country_analysis_report.txt")

# ==========================================
# 步骤8：保存Top频道列表
# ==========================================

print("\n[步骤8] 保存Top频道列表...")

# 保存每个国家的Top 20频道
france_summary.head(20).to_csv('outputs/three_country/france_top20_channels.csv', index=False)
hungary_summary.head(20).to_csv('outputs/three_country/hungary_top20_channels.csv', index=False)
luxembourg_summary.head(20).to_csv('outputs/three_country/luxembourg_top20_channels.csv', index=False)

print("✓ 已保存三个国家的Top 20频道列表")

print("\n" + "="*70)
print("✅ 三国分析完成！")
print("="*70)
print("\n已生成的文件:")
print("  📊 图表:")
print("     - outputs/three_country/01_three_country_comparison.png")
print("     - outputs/three_country/02_distribution_comparison.png")
print("     - outputs/three_country/03_time_series_comparison.png")
print("     - outputs/three_country/04_view_engagement_comparison.png")
print("  📄 报告:")
print("     - outputs/three_country/three_country_analysis_report.txt")
print("  📋 数据:")
print("     - outputs/three_country/france_top20_channels.csv")
print("     - outputs/three_country/hungary_top20_channels.csv")
print("     - outputs/three_country/luxembourg_top20_channels.csv")