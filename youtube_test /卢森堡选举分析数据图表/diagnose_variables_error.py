import pandas as pd

print("=" * 80)
print("诊断: 检查可用变量")
print("=" * 80)

# 加载数据
pre = pd.read_stata("pre-electoral-2023-complet.dta", convert_categoricals=False)
post = pd.read_stata("post-electoral-2023.dta", convert_categoricals=False)
post_foreign = pd.read_stata("post-electoral etrangers.dta", convert_categoricals=False)

# 创建对比数据
post['citizen_type'] = 0
post_foreign['citizen_type'] = 1
common_vars = list(set(post.columns).intersection(set(post_foreign.columns)))
all_respondents = pd.concat([post[common_vars], post_foreign[common_vars]], ignore_index=True)

print(f"\n✅ POST数据: {len(post)} 行, {len(post.columns)} 列")
print(f"✅ POST_FOREIGN数据: {len(post_foreign)} 行, {len(post_foreign.columns)} 列")
print(f"✅ 共同变量数: {len(common_vars)}")
print(f"✅ 合并后数据: {len(all_respondents)} 行, {len(all_respondents.columns)} 列")

# ============================================================
# 检查 M 变量
# ============================================================
print("\n" + "=" * 80)
print("检查 M 开头的变量")
print("=" * 80)

print("\n【POST数据中的M变量】")
m_vars_post = [col for col in post.columns if col.startswith('M')]
print(f"数量: {len(m_vars_post)}")
print(f"变量: {m_vars_post[:20] if m_vars_post else '无'}")

print("\n【POST_FOREIGN数据中的M变量】")
m_vars_foreign = [col for col in post_foreign.columns if col.startswith('M')]
print(f"数量: {len(m_vars_foreign)}")
print(f"变量: {m_vars_foreign[:20] if m_vars_foreign else '无'}")

print("\n【共同的M变量】")
common_m = [col for col in common_vars if col.startswith('M')]
print(f"数量: {len(common_m)}")
print(f"变量: {common_m[:20] if common_m else '无'}")

print("\n【ALL_RESPONDENTS数据中的M变量】")
m_vars_all = [col for col in all_respondents.columns if col.startswith('M')]
print(f"数量: {len(m_vars_all)}")
print(f"变量: {m_vars_all[:20] if m_vars_all else '无'}")

# ============================================================
# 检查 SP 变量
# ============================================================
print("\n" + "=" * 80)
print("检查 SP 开头的变量")
print("=" * 80)

print("\n【共同的SP变量】")
common_sp = [col for col in common_vars if col.startswith('SP')]
print(f"数量: {len(common_sp)}")
print(f"变量: {common_sp[:20] if common_sp else '无'}")

# ============================================================
# 显示所有共同变量
# ============================================================
print("\n" + "=" * 80)
print("所有共同变量列表")
print("=" * 80)

print(f"\n共同变量 ({len(common_vars)} 个):")
for i, var in enumerate(sorted(common_vars), 1):
    print(f"{i:3d}. {var}")

# ============================================================
# 检查哪些变量适合做态度对比
# ============================================================
print("\n" + "=" * 80)
print("推荐用于对比的变量")
print("=" * 80)

# 找出数值型变量,且不是ID或权重
numeric_vars = []
for col in common_vars:
    if col in ['researchId', 'D_WEIGHT', 'citizen_type']:
        continue
    if all_respondents[col].dtype in ['float64', 'int64']:
        n_unique = all_respondents[col].nunique()
        if 2 <= n_unique <= 20:  # 合理的量表范围
            numeric_vars.append({
                'Variable': col,
                'Unique_Values': n_unique,
                'Min': all_respondents[col].min(),
                'Max': all_respondents[col].max(),
                'Mean': all_respondents[col].mean()
            })

numeric_df = pd.DataFrame(numeric_vars)
if len(numeric_df) > 0:
    print(f"\n找到 {len(numeric_df)} 个适合对比的数值变量:")
    print(numeric_df.to_string(index=False))
    
    # 保存推荐变量列表
    numeric_df.to_csv('recommended_variables.csv', index=False)
    print("\n✅ 已保存推荐变量到: recommended_variables.csv")
else:
    print("\n⚠️ 没有找到适合对比的数值变量")

# ============================================================
# 示例分析: 用实际存在的变量
# ============================================================
print("\n" + "=" * 80)
print("示例: 使用实际存在的变量进行对比")
print("=" * 80)

if len(numeric_df) > 0:
    # 选择前3个变量进行示例对比
    sample_vars = numeric_df['Variable'].head(3).tolist()
    
    print(f"\n使用变量: {sample_vars}")
    
    from scipy import stats
    
    results = []
    for var in sample_vars:
        lux = all_respondents[all_respondents['citizen_type'] == 0][var].dropna()
        foreign = all_respondents[all_respondents['citizen_type'] == 1][var].dropna()
        
        if len(lux) > 0 and len(foreign) > 0:
            t_stat, p_value = stats.ttest_ind(lux, foreign)
            
            results.append({
                'Variable': var,
                'Luxembourg_Mean': f"{lux.mean():.3f}",
                'Foreign_Mean': f"{foreign.mean():.3f}",
                'Difference': f"{lux.mean() - foreign.mean():.3f}",
                'T_Statistic': f"{t_stat:.3f}",
                'P_Value': f"{p_value:.4f}",
                'Significant': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
            })
    
    results_df = pd.DataFrame(results)
    print("\n【本国 vs 外国公民对比 (示例)】")
    print(results_df.to_string(index=False))
    
    results_df.to_csv('actual_citizen_comparison.csv', index=False)
    print("\n✅ 已保存实际对比结果到: actual_citizen_comparison.csv")

print("\n" + "=" * 80)
print("诊断完成!")
print("=" * 80)