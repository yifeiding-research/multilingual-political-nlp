import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.stats import spearmanr, kruskal, shapiro

df = pd.read_excel("political_influencers_Luxembourg.xlsx")

print(df.head())

# 清理数据：移除 view_count 为 0 的行
df = df[df['view_count'] > 0].copy()

df["engagement"] = (df["like_count"] + df["comment_count"]) / df["view_count"]

# 移除异常的 engagement 值（>1 或 无穷大）
df = df[(df['engagement'] <= 1) & (df['engagement'].notna())].copy()

channel_engagement = (
    df
    .groupby("channel_name")["engagement"]
    .mean()
    .reset_index()
    .sort_values(by="engagement", ascending=False)
)

print(channel_engagement.head())

top10 = channel_engagement.head(10)
plt.figure(figsize=(10, 6))
plt.barh(top10["channel_name"], top10["engagement"])
plt.xlabel("Average engagement rate")
plt.ylabel("Channel")
plt.title("Top 10 Luxembourg Political YouTube Channels by Engagement")
plt.gca().invert_yaxis()
plt.tight_layout()

df["published_date"] = pd.to_datetime(df["published_date"])
df["year"] = df["published_date"].dt.year
df["month"] = df["published_date"].dt.month

monthly_engagement = (
    df
    .groupby(["year", "month"])["engagement"]
    .mean()
    .reset_index()
)

monthly_engagement["date"] = pd.to_datetime(
    monthly_engagement["year"].astype(str) + "-" +
    monthly_engagement["month"].astype(str) + "-01"
)

plt.figure(figsize=(10, 6))
plt.plot(monthly_engagement["date"], monthly_engagement["engagement"])
plt.xlabel("Time")
plt.ylabel("Average engagement rate")
plt.title("Average YouTube Engagement Over Time (Luxembourg Politics)")
plt.tight_layout()

video_counts = df["channel_name"].value_counts().head(10)
plt.figure(figsize=(10, 6))
plt.barh(video_counts.index, video_counts.values, color='skyblue')
plt.xlabel("Number of videos")
plt.ylabel("Channel")
plt.title("Top 10 Channels by Video Count")
plt.gca().invert_yaxis()
plt.tight_layout()

plt.figure(figsize=(10, 6))
plt.scatter(df["view_count"], df["engagement"], alpha=0.5)
plt.xlabel("View count")
plt.ylabel("Engagement rate")
plt.title("View Count vs Engagement Rate")
plt.xscale('log')
plt.tight_layout()

top5_channels = channel_engagement.head(5)["channel_name"]
top5_data = df[df["channel_name"].isin(top5_channels)]

channel_views = top5_data.groupby("channel_name")["view_count"].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
plt.bar(channel_views.index, channel_views.values, color='coral')
plt.xlabel("Channel")
plt.ylabel("Total views (log scale)")
plt.title("Top 5 Channels by Total Views")
plt.yscale('log')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

print("\n========== 数据统计 ==========")
print(f"总共有 {len(df)} 个视频")
print(f"总共有 {df['channel_name'].nunique()} 个频道")
print(f"\n平均观看量: {df['view_count'].mean():.0f}")
print(f"平均点赞数: {df['like_count'].mean():.0f}")
print(f"平均评论数: {df['comment_count'].mean():.0f}")
print(f"平均互动率: {df['engagement'].mean():.4f}")

# ========== 统计检验 ==========
print("\n========== Descriptive Statistics ==========")
print(df[['view_count', 'like_count', 'comment_count', 'engagement']].describe())

print("\n========== Normality Tests ==========")
for col in ['view_count', 'engagement']:
    sample_data = df[col].dropna()
    if len(sample_data) > 3:
        sample_size = min(5000, len(sample_data))
        stat, p = shapiro(sample_data.sample(sample_size))
        print(f"{col}: W = {stat:.4f}, p = {p:.4f}")

print("\n========== Spearman Correlation: Video Count vs Engagement ==========")
channel_video_counts = df.groupby('channel_name').size()
channel_avg_engagement = df.groupby('channel_name')['engagement'].mean()
# 确保两个序列对齐
aligned_data = pd.DataFrame({
    'video_count': channel_video_counts,
    'avg_engagement': channel_avg_engagement
}).dropna()
if len(aligned_data) > 2:
    corr, p_value = spearmanr(aligned_data['video_count'], aligned_data['avg_engagement'])
    print(f"r_s = {corr:.4f}, p = {p_value:.4f}")
else:
    print("Insufficient data")

print("\n========== Spearman Correlation: View Count vs Engagement ==========")
clean_df = df[['view_count', 'engagement']].dropna()
if len(clean_df) > 2:
    corr2, p_value2 = spearmanr(clean_df['view_count'], clean_df['engagement'])
    print(f"r_s = {corr2:.4f}, p = {p_value2:.4f}")
else:
    print("Insufficient data")

print("\n========== Kruskal-Wallis H Test: Engagement by Channel ==========")
top10_channels = channel_engagement.head(10)['channel_name'].tolist()
top10_data = df[df['channel_name'].isin(top10_channels)]
groups = [group['engagement'].dropna().values for name, group in top10_data.groupby('channel_name')]
groups = [g for g in groups if len(g) > 0]  # 移除空组
if len(groups) >= 2:
    h_stat, p_val = kruskal(*groups)
    print(f"H = {h_stat:.4f}, p = {p_val:.4f}")
else:
    print("Insufficient groups")

print("\n========== 详细分析：View Count vs Engagement ==========")

# 按观看量分四个区间
df['view_quartile'] = pd.qcut(df['view_count'], q=4, labels=['Q1 (低)', 'Q2', 'Q3', 'Q4 (高)'])

print("\n各观看量区间的互动率统计：")
for quartile in ['Q1 (低)', 'Q2', 'Q3', 'Q4 (高)']:
    data = df[df['view_quartile'] == quartile]['engagement']
    print(f"{quartile}: Mean = {data.mean():.4f}, Median = {data.median():.4f}, N = {len(data)}")

# 分别计算每个区间内的相关性
print("\n分区间的相关性：")
for quartile in ['Q1 (低)', 'Q2', 'Q3', 'Q4 (高)']:
    subset = df[df['view_quartile'] == quartile][['view_count', 'engagement']].dropna()
    if len(subset) > 2:
        corr, p = spearmanr(subset['view_count'], subset['engagement'])
        print(f"{quartile}: r_s = {corr:.4f}, p = {p:.4f}")

# 整体相关性（原始数据）
print("\n整体相关性（所有数据）：")
corr_all, p_all = spearmanr(df['view_count'], df['engagement'])
print(f"r_s = {corr_all:.4f}, p = {p_all:.4f}")

# 看看极端值
print("\n极高观看量视频 (top 5%)：")
top5_threshold = df['view_count'].quantile(0.95)
top5_videos = df[df['view_count'] >= top5_threshold]
print(f"平均互动率 = {top5_videos['engagement'].mean():.4f}")

print("\n极低观看量视频 (bottom 5%)：")
bottom5_threshold = df['view_count'].quantile(0.05)
bottom5_videos = df[df['view_count'] <= bottom5_threshold]
print(f"平均互动率 = {bottom5_videos['engagement'].mean():.4f}")
print("\n========== Gini Coefficient for View Count ==========")
def gini(x):
    x = np.array(x)
    x = x[x > 0]  # 移除0值
    if len(x) == 0:
        return np.nan
    sorted_x = np.sort(x)
    n = len(x)
    cumsum = np.cumsum(sorted_x)
    return (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n

gini_coef = gini(df['view_count'].values)
print(f"Gini = {gini_coef:.4f}")

plt.show()