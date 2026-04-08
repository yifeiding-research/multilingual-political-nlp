import pandas as pd
import numpy as np
import re
from datetime import datetime

import statsmodels.formula.api as smf
pre = pd.read_stata("/mnt/data/pre-electoral-2023-complet.dta")
post = pd.read_stata("/mnt/data/post-electoral-2023.dta")
# 确保时间格式
youtube["published_date"] = pd.to_datetime(youtube["published_date"])

# 卢森堡 2023 立法选举日期
election_day = pd.to_datetime("2023-10-08")

# 距离选举日的天数
youtube["days_to_election"] = (
    youtube["published_date"] - election_day
).dt.days

# 选举期：选举日前 90 天
youtube["election_period"] = youtube["days_to_election"].between(-90, 0)
youtube["engagement"] = (
    youtube["like_count"] + youtube["comment_count"]
) / youtube["view_count"]

# 避免除零 & 极端值
youtube = youtube[youtube["view_count"] > 0]
youtube["engagement"] = youtube["engagement"].clip(upper=1)
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zà-ÿäöüßëéèêîïôûçœ\s]", "", text)
    return text

youtube["title_clean"] = youtube["video_title"].apply(clean_text)
policy_words = [
    # EN
    "budget", "tax", "economy", "housing", "pension", "education", "health",
    # FR
    "budget", "impôt", "économie", "logement", "retraite", "éducation", "santé",
    # DE
    "haushalt", "steuer", "wirtschaft", "wohnen", "rente", "bildung", "gesundheit",
    # LU
    "budget", "steier", "wirtschaft", "wunnen", "pensioun", "bildung", "gesondheet"
]

emotion_words = [
    # EN
    "crisis", "danger", "fight", "protect", "future", "freedom", "justice",
    # FR
    "crise", "danger", "lutte", "protéger", "avenir", "liberté", "justice",
    # DE
    "krise", "gefahr", "kampf", "schützen", "zukunft", "freiheit", "gerechtigkeit",
    # LU
    "kris", "gefor", "kampf", "zukunft", "fräiheet", "gerechtigkeit"
]
def contains_words(text, word_list):
    return any(word in text for word in word_list)

youtube["policy_content"] = youtube["title_clean"].apply(
    lambda x: contains_words(x, policy_words)
)

youtube["emotional_content"] = youtube["title_clean"].apply(
    lambda x: contains_words(x, emotion_words)
)
# 视频发布年份（控制时间趋势）
youtube["year"] = youtube["published_date"].dt.year

# 对数播放量（规模控制）
youtube["log_views"] = np.log(youtube["view_count"])
m1 = smf.ols(
    "engagement ~ election_period + log_views + C(year)",
    data=youtube
).fit(cov_type="HC3")

print(m1.summary())
m2 = smf.ols(
    "engagement ~ election_period + emotional_content + policy_content + log_views + C(year)",
    data=youtube
).fit(cov_type="HC3")

print(m2.summary())
m3 = smf.ols(
    "engagement ~ election_period * emotional_content + policy_content + log_views + C(year)",
    data=youtube
).fit(cov_type="HC3")

print(m3.summary())
