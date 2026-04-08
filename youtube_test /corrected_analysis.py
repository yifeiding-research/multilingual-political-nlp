import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf

print("=" * 80)
print("卢森堡2023选举研究 - 修正版分析")
print("=" * 80)

# ============================================================
# 数据加载
# ============================================================
pre = pd.read_stata("pre-electoral-2023-complet.dta", convert_categoricals=False)
post = pd.read_stata("post-electoral-2023.dta", convert_categoricals=False)
post_foreign = pd.read_stata("post-electoral etrangers.dta", convert_categoricals=False)

# 创建 Panel 数据 (选前+选后本国)
panel = pd.merge(pre, post, on='researchId', how='inner', suffixes=('_pre', '_post'))

# 创建选前对比数据 (本国vs外国)
pre_lux = pre.copy()
pre_lux['citizen_type'] = 0
pre_foreign = post_foreign.copy()
pre_foreign['citizen_type'] = 1

# 找共同变量
common_vars = list(set(pre_lux.columns).intersection(set(pre_foreign.columns)))
pre_comparison = pd.concat([pre_lux[common_vars], pre_foreign[common_vars]], ignore_index=True)

print(f"✅ Panel数据 (选前+选后本国): {len(panel)} 观测")
print(f"✅ 选前对比数据 (本国+外国): {len(pre_comparison)} 观测")
print(f"✅ 共同变量数: {len(common_vars)}\n")

# ============================================================
# 研究1: 政治兴趣的稳定性 (选前 vs 选后)
# ============================================================
print("\n" + "=" * 80)
print("研究1: 政治兴趣的稳定性 (本国公民)")
print("=" * 80)

panel['political_interest_pre'] = panel['SP1']
panel['political_interest_post'] = panel['Q1']

# 交叉表
print("\n【选前政治兴趣 vs 选后政治兴趣 交叉表】")
crosstab = pd.crosstab(
    panel['political_interest_pre'], 
    panel['political_interest_post'],
    margins=True
)
print(crosstab)

# 相关系数
corr = panel[['political_interest_pre', 'political_interest_post']].corr()
print(f"\n相关系数: {corr.iloc[0,1]:.3f}")

# 配对 t 检验
valid_data = panel[['political_interest_pre', 'political_interest_post']].dropna()
t_stat, p_value = stats.ttest_rel(
    valid_data['political_interest_pre'], 
    valid_data['political_interest_post']
)
print(f"配对t检验: t={t_stat:.3f}, p={p_value:.4f}")
print(f"解读: 选前政治兴趣(M={valid_data['political_interest_pre'].mean():.2f}) vs 选后(M={valid_data['political_interest_post'].mean():.2f})")

# 回归分析
model1 = smf.ols(
    'political_interest_post ~ political_interest_pre + D_SEXE_post + D_CAT_AGE_post + D_REVENU_post',
    data=panel
).fit(cov_type='HC3')

print("\n【回归模型1: 预测选后政治兴趣】")
print(model1.summary())

# ============================================================
# 研究2: 本国 vs 外国公民的政治态度差异 (选前数据)
# ============================================================
print("\n" + "=" * 80)
print("研究2: 本国 vs 外国公民的政治态度差异 (选前)")
print("=" * 80)

# M变量在选前数据中
attitude_vars = ['M1', 'M2', 'M3_1', 'M3_2', 'M4_1', 'M4_2']

results = []
for var in attitude_vars:
    if var in pre_comparison.columns:
        lux = pre_comparison[pre_comparison['citizen_type'] == 0][var].dropna()
        foreign = pre_comparison[pre_comparison['citizen_type'] == 1][var].dropna()
        
        if len(lux) > 0 and len(foreign) > 0:
            t_stat, p_val = stats.ttest_ind(lux, foreign)
            
            results.append({
                'Variable': var,
                'Luxembourg_Mean': lux.mean(),
                'Luxembourg_SD': lux.std(),
                'Foreign_Mean': foreign.mean(),
                'Foreign_SD': foreign.std(),
                'Difference': lux.mean() - foreign.mean(),
                'T_Statistic': t_stat,
                'P_Value': p_val,
                'Sig': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
            })

results_df = pd.DataFrame(results)
print("\n【本国 vs 外国公民态度对比】")
print(results_df.to_string(index=False))

# 回归分析: 控制人口统计学变量
if 'M1' in pre_comparison.columns:
    model2 = smf.ols(
        'M1 ~ citizen_type + D_SEXE + D_CAT_AGE + D_REVENU + D_OCCUPATION',
        data=pre_comparison
    ).fit(cov_type='HC3')
    
    print("\n【回归模型2: M1态度 ~ 公民类型 + 控制变量】")
    print(model2.summary())
    
    # 解读
    coef = model2.params['citizen_type']
    pval = model2.pvalues['citizen_type']
    print(f"\n解读: 外国公民的M1态度比本国公民 {'高' if coef > 0 else '低'} {abs(coef):.3f} 分")
    print(f"      (p={'<0.001' if pval < 0.001 else f'={pval:.3f}'})")

# ============================================================
# 研究3: 人口统计学因素对政治参与的影响
# ============================================================
print("\n" + "=" * 80)
print("研究3: 人口统计学对政治参与的影响")
print("=" * 80)

# 创建因变量
panel['interest_reversed'] = 5 - panel['SP1']  # 越高越感兴趣
panel['will_vote'] = (panel['SP3'] == 1).astype(float)

print("\n【政治参与指标描述】")
print(panel[['interest_reversed', 'will_vote']].describe())

print(f"\n投票意向: {panel['will_vote'].sum()}/{len(panel)} ({panel['will_vote'].mean()*100:.1f}%)")

# Logistic回归: 预测是否打算投票
# 检查列名
demo_vars = []
for base in ['D_SEXE', 'D_CAT_AGE', 'D_REVENU', 'D_OCCUPATION']:
    if base in panel.columns:
        demo_vars.append(base)
    elif base + '_pre' in panel.columns:
        demo_vars.append(base + '_pre')

if len(demo_vars) >= 2:
    formula = 'will_vote ~ ' + ' + '.join(demo_vars)
    print(f"\n使用公式: {formula}")
    model3a = smf.logit(formula, data=panel).fit()
    print("\n【Logistic回归: 预测投票意向】")
    print(model3a.summary())
else:
    print("⚠️ 缺少必要变量,跳过Logistic回归")
    model3a = None

print("\n【Logistic回归: 预测投票意向】")
print(model3a.summary())

# 计算边际效应
print("\n【边际效应 (Odds Ratios)】")
odds_ratios = np.exp(model3a.params)
print(odds_ratios)

# OLS回归: 预测政治兴趣
model3b = smf.ols(
    'interest_reversed ~ D_SEXE + D_CAT_AGE + D_REVENU + D_OCCUPATION',
    data=panel
).fit(cov_type='HC3')

# OLS回归: 预测政治兴趣
if len(demo_vars) >= 2 and 'interest_reversed' in panel.columns:
    formula = 'interest_reversed ~ ' + ' + '.join(demo_vars)
    print(f"\n使用公式: {formula}")
    model3b = smf.ols(formula, data=panel).fit(cov_type='HC3')
    print("\n【OLS回归: 预测政治兴趣】")
    print(model3b.summary())
else:
    print("⚠️ 缺少必要变量,跳过OLS回归")
    model3b = None

# ============================================================
# 研究4: 政党评价分析 (SP11系列)
# ============================================================
print("\n" + "=" * 80)
print("研究4: 政党评价的差异")
print("=" * 80)

# SP11_1 到 SP11_12 是不同政党的评分
sp11_vars = [f'SP11_{i}' for i in range(1, 13) if f'SP11_{i}' in pre_comparison.columns]

if sp11_vars:
    print(f"\n分析 {len(sp11_vars)} 个政党评分")
    
    party_results = []
    for var in sp11_vars:
        lux = pre_comparison[pre_comparison['citizen_type'] == 0][var].dropna()
        foreign = pre_comparison[pre_comparison['citizen_type'] == 1][var].dropna()
        
        if len(lux) > 0 and len(foreign) > 0:
            t_stat, p_val = stats.ttest_ind(lux, foreign)
            
            party_results.append({
                'Party_Variable': var,
                'Lux_Mean': lux.mean(),
                'Foreign_Mean': foreign.mean(),
                'Diff': lux.mean() - foreign.mean(),
                'P_Value': p_val,
                'Sig': '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else 'ns'
            })
    
    party_df = pd.DataFrame(party_results)
    print("\n【政党评分对比: 本国 vs 外国】")
    print(party_df.to_string(index=False))
    
    party_df.to_csv('party_evaluation_comparison.csv', index=False)

# ============================================================
# 导出所有结果
# ============================================================
print("\n" + "=" * 80)
print("导出结果")
print("=" * 80)

# 1. 描述性统计
desc_stats = panel[['political_interest_pre', 'political_interest_post', 
                     'interest_reversed', 'will_vote']].describe()
desc_stats.to_csv('descriptive_statistics.csv')

# 2. 态度对比
results_df.to_csv('attitude_comparison.csv', index=False)

# 3. 回归结果
with open('regression_results.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("模型1: 预测选后政治兴趣\n")
    f.write("=" * 80 + "\n")
    f.write(str(model1.summary()))
    f.write("\n\n")
    
    if 'M1' in pre_comparison.columns:
        f.write("=" * 80 + "\n")
        f.write("模型2: M1态度 ~ 公民类型\n")
        f.write("=" * 80 + "\n")
        f.write(str(model2.summary()))
        f.write("\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("模型3a: Logistic回归 - 投票意向\n")
    f.write("=" * 80 + "\n")
    f.write(str(model3a.summary()))
    f.write("\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("模型3b: OLS回归 - 政治兴趣\n")
    f.write("=" * 80 + "\n")
    f.write(str(model3b.summary()))

print("✅ 已保存:")
print("  - descriptive_statistics.csv (描述性统计)")
print("  - attitude_comparison.csv (态度对比)")
print("  - party_evaluation_comparison.csv (政党评价对比)")
print("  - regression_results.txt (完整回归结果)")

# ============================================================
# 研究发现总结
# ============================================================
print("\n" + "=" * 80)
print("研究发现总结")
print("=" * 80)

summary = f"""
【研究1: 政治兴趣稳定性】
- 样本量: {len(valid_data)}
- 选前平均: {valid_data['political_interest_pre'].mean():.2f}
- 选后平均: {valid_data['political_interest_post'].mean():.2f}
- 相关系数: {corr.iloc[0,1]:.3f}
- 配对t检验: t={t_stat:.3f}, p={p_value:.4f}
- 结论: {'政治兴趣在选举前后有显著变化' if p_value < 0.05 else '政治兴趣相对稳定'}

【研究2: 本国vs外国公民态度】
- 分析变量: {len(results_df)}个态度变量
- 显著差异数: {len(results_df[results_df['Sig'] != 'ns'])}
- 最大差异: {results_df.loc[results_df['Difference'].abs().idxmax(), 'Variable']} (diff={results_df['Difference'].abs().max():.3f})

【研究3: 人口统计学影响】
- 投票率: {panel['will_vote'].mean()*100:.1f}%
- 年龄效应: {'显著' if model3b.pvalues.get('D_CAT_AGE', 1) < 0.05 else '不显著'}
- 性别效应: {'显著' if model3b.pvalues.get('D_SEXE', 1) < 0.05 else '不显著'}
- 收入效应: {'显著' if model3b.pvalues.get('D_REVENU', 1) < 0.05 else '不显著'}

【研究4: 政党评价】
- 分析政党数: {len(sp11_vars) if sp11_vars else 0}
- 显著差异数: {len(party_df[party_df['Sig'] != 'ns']) if sp11_vars else 0}

建议后续分析:
1. 深入分析具体哪些政党在本国/外国公民中评价差异大
2. 分析M变量(态度)的具体含义(需要codebook)
3. 考虑年龄和收入的交互效应
4. 可视化关键发现
"""

print(summary)

with open('research_summary.txt', 'w', encoding='utf-8') as f:
    f.write(summary)

print("\n✅ 已保存: research_summary.txt")

print("\n" + "=" * 80)
print("分析完成! 🎉")
print("=" * 80)