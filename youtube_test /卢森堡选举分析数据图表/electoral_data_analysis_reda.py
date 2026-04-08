import pandas as pd
import numpy as np

# 正确的文件路径 + 修复分类变量问题
pre = pd.read_stata(
    "pre-electoral-2023-complet.dta",
    convert_categoricals=False  # 关键修复
)

post = pd.read_stata(
    "post-electoral-2023.dta",
    convert_categoricals=False
)

post_foreign = pd.read_stata(
    "post-electoral etrangers.dta",
    convert_categoricals=False
)

# 查看数据基本信息
print("=" * 60)
print("PRE-ELECTORAL 数据")
print("=" * 60)
print(f"观测数: {len(pre)}")
print(f"变量数: {len(pre.columns)}")
print(f"\n前5行预览:")
print(pre.head())
print(f"\n所有变量名:")
print(pre.columns.tolist())
print(f"\n数据类型:")
print(pre.dtypes)

print("\n" + "=" * 60)
print("POST-ELECTORAL 数据")
print("=" * 60)
print(f"观测数: {len(post)}")
print(f"变量数: {len(post.columns)}")
print(f"\n前5行预览:")
print(post.head())
print(f"\n所有变量名:")
print(post.columns.tolist())

print("\n" + "=" * 60)
print("POST-ELECTORAL ÉTRANGERS 数据")
print("=" * 60)
print(f"观测数: {len(post_foreign)}")
print(f"变量数: {len(post_foreign.columns)}")
print(f"\n前5行预览:")
print(post_foreign.head())
print(f"\n所有变量名:")
print(post_foreign.columns.tolist())

# 检查是否有共同的ID可以连接数据
print("\n" + "=" * 60)
print("数据连接可能性检查")
print("=" * 60)

# 查找可能的ID变量
pre_cols = set(pre.columns)
post_cols = set(post.columns)
common_cols = pre_cols.intersection(post_cols)

print(f"\nPre和Post共同变量 ({len(common_cols)} 个):")
print(sorted(list(common_cols)))

# 检查是否有唯一标识符
potential_ids = [col for col in pre.columns if 'id' in col.lower() or 'identifier' in col.lower()]
print(f"\n潜在的ID变量:")
print(potential_ids)
# 保存为CSV
pre.to_csv("pre_electoral_2023.csv", index=False)
post.to_csv("post_electoral_2023.csv", index=False)
post_foreign.to_csv("post_electoral_foreign_2023.csv", index=False)

print("\n✅ 数据已保存为CSV格式")