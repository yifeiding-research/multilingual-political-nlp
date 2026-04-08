import pandas as pd
import numpy as np
from datetime import datetime

print("\n" + "="*70)
print("🔄 数据整合程序")
print("="*70)

# ==========================================
# 步骤1：加载主数据文件
# ==========================================

print("\n[步骤1] 加载各国频道级别的原始视频数据...")

# 加载视频级数据（来自最完整的文件）
df_final = pd.read_excel('final_dataset_corrected.xlsx')

print(f"✓ 加载了 {len(df_final)} 条视频记录")
print(f"  包含 {df_final['country'].nunique()} 个国家")
print(f"  包含 {df_final['channel_name'].nunique()} 个频道")
print(f"  时间范围: {df_final['published_date'].min()} 到 {df_final['published_date'].max()}")

# ==========================================
# 步骤2：生成频道级汇总数据
# ==========================================

print("\n[步骤2] 生成频道级汇总数据...")

# 按频道汇总统计
agg_dict = {
    'view_count': ['sum', 'mean', 'count'],
    'like_count': ['sum', 'mean'],
    'comment_count': ['sum', 'mean'],
}

# 如果有这些列才加进去
if 'is_multilingual' in df_final.columns:
    agg_dict['is_multilingual'] = 'mean'
if 'num_languages' in df_final.columns:
    agg_dict['num_languages'] = 'mean'
if 'engagement_rate' in df_final.columns:
    agg_dict['engagement_rate'] = 'mean'
if 'primary_language' in df_final.columns:
    agg_dict['primary_language'] = lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown'

channel_summary = df_final.groupby(['country', 'channel_id', 'channel_name']).agg(agg_dict).reset_index()

# 展平多级列名
new_columns = ['country', 'channel_id', 'channel_name']
new_columns += ['total_views', 'avg_views_per_video', 'total_videos',
                'total_likes', 'avg_likes_per_video',
                'total_comments', 'avg_comments_per_video']

# 添加可选列的名称
optional_cols = []
if 'is_multilingual' in agg_dict:
    optional_cols.append('multilingual_content_rate')
if 'num_languages' in agg_dict:
    optional_cols.append('avg_num_languages')
if 'engagement_rate' in agg_dict:
    optional_cols.append('avg_engagement_rate')
if 'primary_language' in agg_dict:
    optional_cols.append('primary_language')

new_columns.extend(optional_cols)
channel_summary.columns = new_columns[:len(channel_summary.columns)]

# 计算订阅者数（假设根据总观看数推算）
# 这是一个启发式方法，如果你有真实的subscriber_count，可以替换
channel_summary['subscriber_count'] = (channel_summary['total_views'] / 1000).astype(int)

print(f"✓ 生成了 {len(channel_summary)} 个频道的汇总数据")
print(f"\n频道数分布:")
print(channel_summary['country'].value_counts())

# ==========================================
# 步骤3：添加政治立场和其他信息
# ==========================================

print("\n[步骤3] 添加政治立场信息...")

# 根据频道名称和内容推断政治立场
# 这需要你的定义 - 现在用启发式方法
def infer_political_stance(channel_name, country):
    """
    根据频道名称推断政治立场
    这是示例，你可以根据实际情况修改
    """
    channel_lower = channel_name.lower()
    
    # 匈牙利的opposition频道特征
    if country == 'Hungary':
        opposition_keywords = ['kritika', 'orbán', 'magyar közösség', 'momentum', 'dk']
        if any(kw in channel_lower for kw in opposition_keywords):
            return 'opposition'
        return 'independent'
    
    # 法国
    if country == 'France':
        opposition_keywords = ['contre', 'critique', 'nupes', 'lr']
        if any(kw in channel_lower for kw in opposition_keywords):
            return 'opposition'
        return 'independent'
    
    # 卢森堡
    if country == 'Luxembourg':
        opposition_keywords = ['csv', 'grond', 'déi lénk']
        if any(kw in channel_lower for kw in opposition_keywords):
            return 'opposition'
        return 'independent'
    
    return 'other'

channel_summary['political_stance'] = channel_summary.apply(
    lambda row: infer_political_stance(row['channel_name'], row['country']),
    axis=1
)

print("✓ 已添加政治立场信息")
print(f"\n政治立场分布:")
print(channel_summary['political_stance'].value_counts())

# ==========================================
# 步骤4：添加民主质量指标
# ==========================================

print("\n[步骤4] 添加民主质量指标...")

# V-Dem民主指数（2024年）
democracy_scores = {
    'Luxembourg': 0.85,
    'France': 0.75,
    'Hungary': 0.42
}

channel_summary['democracy_index'] = channel_summary['country'].map(democracy_scores)

print("✓ 已添加民主质量指标")
for country, score in democracy_scores.items():
    print(f"  {country}: {score}")

# ==========================================
# 步骤5：计算关键指标
# ==========================================

print("\n[步骤5] 计算关键分析指标...")

# 确保有engagement_rate列
if 'engagement_rate' not in channel_summary.columns:
    # 计算参与率 = (点赞 + 评论) / 观看数 * 100
    channel_summary['engagement_rate'] = (
        (channel_summary['total_likes'] + channel_summary['total_comments']) / 
        channel_summary['total_views']
    ) * 100
else:
    # 如果存在但都是NaN，则重新计算
    if channel_summary['engagement_rate'].isna().all():
        channel_summary['engagement_rate'] = (
            (channel_summary['total_likes'] + channel_summary['total_comments']) / 
            channel_summary['total_views']
        ) * 100

# 标准化参与率（按人口）
population = {
    'Luxembourg': 0.67,
    'France': 67.0,
    'Hungary': 9.7
}

channel_summary['population_millions'] = channel_summary['country'].map(population)
channel_summary['normalized_engagement_rate'] = (
    channel_summary['engagement_rate'] * 
    (channel_summary['population_millions'] / 10.0)
)

# 多语言内容率（转换为百分比）
channel_summary['multilingual_content_rate'] = (
    channel_summary['multilingual_content_rate'] * 100
)

print("✓ 已计算关键指标")

# ==========================================
# 步骤6：生成政府批评率（基于情绪分析）
# ==========================================

print("\n[步骤6] 从视频数据生成政府批评率...")

# 加载有sentiment的数据
df_sentiment = pd.read_excel('complete_dataset_with_sentiment.xlsx')

# 计算每个频道的critical sentiment比例
criticism_by_channel = df_sentiment.groupby('channel_id').apply(
    lambda x: (x['sentiment'] == 'critical').sum() / len(x) * 100
).reset_index(name='government_criticism_rate')

# 合并到channel_summary
channel_summary = channel_summary.merge(
    criticism_by_channel,
    on='channel_id',
    how='left'
)

# 如果某些频道没有sentiment数据，用平均值填充
channel_summary['government_criticism_rate'].fillna(
    channel_summary.groupby('country')['government_criticism_rate'].transform('mean'),
    inplace=True
)

print("✓ 已计算政府批评率")
print(f"\n各国平均政府批评率:")
print(channel_summary.groupby('country')['government_criticism_rate'].mean().round(2))

# ==========================================
# 步骤7：添加语言分布信息
# ==========================================

print("\n[步骤7] 添加语言分布信息...")

# 如果primary_language不存在，则创建
if 'primary_language' not in channel_summary.columns:
    # 从原始数据中提取primary_language
    primary_lang_by_channel = df_final.groupby('channel_id')['primary_language'].agg(lambda x: x.mode()[0] if len(x.mode()) > 0 else 'unknown').reset_index()
    channel_summary = channel_summary.merge(primary_lang_by_channel, on='channel_id', how='left')
    channel_summary['primary_language'].fillna('unknown', inplace=True)
else:
    channel_summary['primary_language'] = channel_summary['primary_language'].fillna('unknown')

# num_languages 应该已经存在于 channel_summary，但如果不存在就填充
if 'num_languages' not in channel_summary.columns:
    channel_summary['num_languages'] = 1
else:
    channel_summary['num_languages'] = channel_summary['num_languages'].fillna(1)

print("✓ 已添加语言信息")

# ==========================================
# 步骤8：添加数据收集日期
# ==========================================

print("\n[步骤8] 添加元数据...")

channel_summary['data_collection_date'] = '2025-12-28'
channel_summary['data_source'] = 'YouTube API'

# ==========================================
# 步骤9：选择最终列并保存
# ==========================================

print("\n[步骤9] 整理最终输出格式...")

# 选择关键列（按你的需求）
final_columns = [
    'country',
    'channel_id',
    'channel_name',
    'subscriber_count',
    'total_videos',
    'total_views',
    'avg_views_per_video',
    'engagement_rate',
    'normalized_engagement_rate',
    'government_criticism_rate',
    'multilingual_content_rate',
    'avg_num_languages',
    'primary_language',
    'political_stance',
    'democracy_index',
    'avg_likes_per_video',
    'avg_comments_per_video',
    'data_collection_date'
]

# 只保留存在的列
final_columns = [col for col in final_columns if col in channel_summary.columns]

channel_data = channel_summary[final_columns].copy()

# 排序和清理
channel_data = channel_data.sort_values(['country', 'channel_name'])
channel_data = channel_data.reset_index(drop=True)

# ==========================================
# 步骤10：保存为CSV
# ==========================================

print("\n[步骤10] 保存最终数据...")

channel_data.to_csv('data/channels_data.csv', index=False)
print(f"✓ 已保存频道数据: data/channels_data.csv")
print(f"  总行数: {len(channel_data)}")
print(f"  总列数: {len(channel_data.columns)}")

# ==========================================
# 步骤11：生成时间序列数据
# ==========================================

print("\n[步骤11] 生成时间序列数据...")

# 按月聚合数据
df_final['published_date'] = pd.to_datetime(df_final['published_date'])
df_final['year_month'] = df_final['published_date'].dt.to_period('M')

time_series = df_final.groupby(['country', 'year_month']).agg({
    'view_count': 'mean',
    'like_count': 'mean',
    'comment_count': 'mean',
    'engagement_rate': 'mean',
    'is_multilingual': 'mean',
    'channel_id': 'nunique'
}).reset_index()

time_series.columns = [
    'country', 'month', 'avg_views', 'avg_likes',
    'avg_comments', 'avg_engagement_rate',
    'multilingual_rate', 'num_channels'
]

time_series['month'] = time_series['month'].astype(str)

time_series.to_csv('data/time_series_data.csv', index=False)
print(f"✓ 已保存时间序列数据: data/time_series_data.csv")
print(f"  总行数: {len(time_series)}")

# ==========================================
# 步骤12：显示摘要统计
# ==========================================

print("\n" + "="*70)
print("📊 数据摘要")
print("="*70)

print("\n频道数量:")
print(channel_data['country'].value_counts().sort_index())

print("\n各国平均参与率:")
print(channel_data.groupby('country')['engagement_rate'].mean().round(2))

print("\n各国平均政府批评率:")
print(channel_data.groupby('country')['government_criticism_rate'].mean().round(2))

print("\n各国多语言内容率:")
print(channel_data.groupby('country')['multilingual_content_rate'].mean().round(2))

print("\n政治立场分布:")
print(channel_data.groupby(['country', 'political_stance']).size())

print("\n" + "="*70)
print("✅ 数据整合完成！")
print("="*70)
print("\n已创建的文件:")
print("  1. data/channels_data.csv - 频道级汇总数据")
print("  2. data/time_series_data.csv - 时间序列数据")
print("\n现在可以开始分析了！")