import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf

print("=" * 80)
print("卢森堡2023选举研究 - 完整分析")
print("=" * 80)

# ============================================================
# 数据加载
# ============================================================
pre = pd.read_stata("pre-electoral-2023-complet.dta", convert_categoricals=False)
post = pd.read_stata("post-electoral-2023.dta", convert_categoricals=False)
post_foreign = pd.read_stata("post-electoral etrangers.dta", convert_categoricals=False)

# 创建 Panel 数据
panel = pd.merge(pre, post, on='researchId', how='inner', suffixes=('_pre', '_post'))

# 创建本国vs外国公民对比数据
post['citizen_type'] = 0
post_foreign['citizen_type'] = 1
common_vars = list(set(post.columns).intersection(set(post_foreign.columns)))
all_respondents = pd.concat([post[common_vars], post_foreign[common_vars]], ignore_index=True)

print(f"✅ Panel数据: {len(panel)} 观测")
print(f"✅ 所有受访者: {len(all_respondents)} 观测\n")

# 先检查变量名
print("Panel数据列名示例:", list(panel.columns[:20]))

# ============================================================
# 研究1: 政治兴趣的稳定性
# ============================================================
print("\n" + "=" * 80)
print("研究1: 政治兴趣的稳定性")
print("=" * 80)

# 检查变量名
if 'SP1_pre' in panel.columns:
    panel['political_interest_pre'] = panel['SP1_pre']
elif 'SP1' in panel.columns:
    panel['political_interest_pre'] = panel['SP1']
else:
    print("警告: 找不到 SP1 变量")
    panel['political_interest_pre'] = None

panel['political_interest_post'] = panel['Q1']

# 交叉表
print("\n【选前政治兴趣 vs 选后政治兴趣 交叉表】")
crosstab = pd.crosstab(panel['political_interest_pre'], panel['political_interest_post'])
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

# 回归分析
model1 = smf.ols(
    'political_interest_post ~ political_interest_pre + D_SEXE_post + D_CAT_AGE_post + D_REVENU_post',
    data=panel
).fit(cov_type='HC3')

print("\n【回归模型1: 预测选后政治兴趣】")
print(model1.summary())

# ============================================================
# 研究2: 本国 vs 外国公民的政治态度差异
# ============================================================
print("\n" + "=" * 80)
print("研究2: 本国 vs 外国公民的政治态度差异")
print("=" * 80)

attitude_vars = ['M1', 'M2', 'M3_1', 'M3_2']

results = []
for var in attitude_vars:
    if var in all_respondents.columns:
        lux = all_respondents[all_respondents['citizen_type'] == 0][var].dropna()
        foreign = all_respondents[all_respondents['citizen_type'] == 1][var].dropna()
        
        if len(lux) > 0 and len(foreign) > 0:
            t_stat, p_value = stats.ttest_ind(lux, foreign)
            
            results.append({
                'Variable': var,
                'Luxembourg_Mean': lux.mean(),
                'Foreign_Mean': foreign.mean(),
                'Difference': lux.mean() - foreign.mean(),
                'T_Statistic': t_stat,
                'P_Value': p_value,
                'Significant': '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
            })

results_df = pd.DataFrame(results)
print("\n【本国 vs 外国公民态度对比】")
print(results_df.to_string(index=False))

# 回归分析
if 'M1' in all_respondents.columns:
    model2 = smf.ols(
        'M1 ~ citizen_type + D_SEXE + D_CAT_AGE + D_REVENU',
        data=all_respondents
    ).fit(cov_type='HC3')
    
    print("\n【回归模型2: M1态度 ~ 公民类型 + 控制变量】")
    print(model2.summary())

# ============================================================
# 研究3: 人口统计学因素对政治参与的影响
# ============================================================
print("\n" + "=" * 80)
print("研究3: 人口统计学对政治参与的影响")
print("=" * 80)

# 检查 SP1 和 SP3 变量
sp1_col = 'SP1_pre' if 'SP1_pre' in panel.columns else 'SP1' if 'SP1' in panel.columns else None
sp3_col = 'SP3_pre' if 'SP3_pre' in panel.columns else 'SP3' if 'SP3' in panel.columns else None

if sp1_col:
    panel['interest_reversed'] = 5 - panel[sp1_col]
else:
    print("警告: 找不到 SP1 变量")

if sp3_col:
    panel['will_vote'] = (panel[sp3_col] == 1).astype(float)
else:
    print("警告: 找不到 SP3 变量")

print("\n【政治参与指标描述】")
print(panel[['interest_reversed', 'will_vote']].describe())

# Logistic回归
demo_cols_pre = []
for col in ['D_SEXE', 'D_CAT_AGE', 'D_REVENU', 'D_OCCUPATION']:
    if col + '_pre' in panel.columns:
        demo_cols_pre.append(col + '_pre')
    elif col in panel.columns:
        demo_cols_pre.append(col)

if demo_cols_pre and 'will_vote' in panel.columns:
    formula = 'will_vote ~ ' + ' + '.join(demo_cols_pre)
    model3a = smf.logit(formula, data=panel).fit()
    print("\n【Logistic回归: 预测投票意向】")
    print(model3a.summary())
else:
    print("警告: 缺少必要的变量进行Logistic回归")

# OLS回归
if demo_cols_pre and 'interest_reversed' in panel.columns:
    formula = 'interest_reversed ~ ' + ' + '.join(demo_cols_pre)
    model3b = smf.ols(formula, data=panel).fit(cov_type='HC3')
    print("\n【OLS回归: 预测政治兴趣】")
    print(model3b.summary())
else:
    print("警告: 缺少必要的变量进行OLS回归")

# ============================================================
# 导出结果
# ============================================================
print("\n" + "=" * 80)
print("导出结果")
print("=" * 80)

desc_stats = panel[['political_interest_pre', 'political_interest_post', 
                     'interest_reversed', 'will_vote']].describe()
desc_stats.to_csv('descriptive_statistics.csv')

results_df.to_csv('citizen_comparison.csv', index=False)

with open('regression_results.txt', 'w') as f:
    f.write(str(model1.summary()))

print("✅ 已保存:")
print("  - descriptive_statistics.csv")
print("  - citizen_comparison.csv")
print("  - regression_results.txt")

print("\n" + "=" * 80)
print("分析完成! 🎉")
print("=" * 80)