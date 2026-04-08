import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================
# 1. 数据加载与准备
# ============================================================

print("=" * 60)
print("数据加载中...")
print("=" * 60)

pre = pd.read_stata("pre-electoral-2023-complet.dta", convert_categoricals=False)
post = pd.read_stata("post-electoral-2023.dta", convert_categoricals=False)
post_foreign = pd.read_stata("post-electoral etrangers.dta", convert_categoricals=False)

print(f"✅ Pre-electoral: {len(pre)} 观测")
print(f"✅ Post-electoral: {len(post)} 观测")
print(f"✅ Post-electoral (外国人): {len(post_foreign)} 观测")

# ============================================================
# 2. 创建Panel数据 (选前-选后匹配)
# ============================================================

print("\n" + "=" * 60)
print("创建Panel数据...")
print("=" * 60)

panel = pd.merge(
    pre, 
    post, 
    on='researchId', 
    how='inner',
    suffixes=('_pre', '_post')
)

print(f"✅ 成功匹配 {len(panel)} 个受访者 (选前+选后)")
print(f"   匹配率: {len(panel)/len(pre)*100:.1f}%")

# ============================================================
# 3. 本国公民 vs 外国公民对比数据
# ============================================================

print("\n" + "=" * 60)
print("合并本国公民与外国公民数据...")
print("=" * 60)

# 标记来源
post['citizen_type'] = 'Luxembourg'
post_foreign['citizen_type'] = 'Foreign'

# 找到共同变量
common_vars = list(set(post.columns).intersection(set(post_foreign.columns)))
print(f"✅ 共同变量数: {len(common_vars)}")

# 合并
all_respondents = pd.concat([
    post[common_vars], 
    post_foreign[common_vars]
], ignore_index=True)

print(f"✅ 总样本: {len(all_respondents)} (本国: {len(post)}, 外国: {len(post_foreign)})")

# ============================================================
# 4. 描述性统计
# ============================================================

print("\n" + "=" * 60)
print("描述性统计")
print("=" * 60)

# 性别分布
print("\n【性别分布】")
if 'D_SEXE' in panel.columns:
    print(panel['D_SEXE_post'].value_counts())

# 年龄分布
print("\n【年龄分布】")
if 'D_CAT_AGE' in panel.columns:
    print(panel['D_CAT_AGE_post'].value_counts())

# 国籍分布
print("\n【本国 vs 外国公民】")
print(all_respondents['citizen_type'].value_counts())

# ============================================================
# 5. 研究问题 1: 投票意向稳定性分析
# ============================================================

print("\n" + "=" * 60)
print("研究1: 投票意向稳定性")
print("=" * 60)

# 寻找投票相关变量
vote_vars_pre = [col for col in panel.columns if 'SP' in col and '_pre' in col]
vote_vars_post = [col for col in panel.columns if 'Q' in col and '_post' in col and 'vote' in col.lower()]

print(f"\n选前可能的投票变量 (SP开头): {len(vote_vars_pre)} 个")
print(f"示例: {vote_vars_pre[:5]}")

print(f"\n选后可能的投票变量 (Q开头): {len(vote_vars_post)} 个")
print(f"示例: {vote_vars_post[:5]}")

# ============================================================
# 6. 研究问题 2: 本国 vs 外国公民态度差异
# ============================================================

print("\n" + "=" * 60)
print("研究2: 本国 vs 外国公民比较")
print("=" * 60)

# 态度变量 (M开头通常是态度量表)
attitude_vars = [col for col in common_vars if col.startswith('M') and '_' in col]
print(f"\n态度变量数: {len(attitude_vars)}")
print(f"示例: {attitude_vars[:10]}")

# 政治参与变量 (SP开头)
participation_vars = [col for col in common_vars if col.startswith('SP')]
print(f"\n政治参与变量数: {len(participation_vars)}")
print(f"示例: {participation_vars[:10]}")

# ============================================================
# 7. 示例分析: T检验比较
# ============================================================

print("\n" + "=" * 60)
print("示例分析: 本国 vs 外国公民态度对比")
print("=" * 60)

# 选择一个态度变量进行示例分析
if 'M1' in all_respondents.columns:
    lux = all_respondents[all_respondents['citizen_type'] == 'Luxembourg']['M1'].dropna()
    foreign = all_respondents[all_respondents['citizen_type'] == 'Foreign']['M1'].dropna()
    
    if len(lux) > 0 and len(foreign) > 0:
        t_stat, p_value = stats.ttest_ind(lux, foreign)
        
        print(f"\n变量: M1")
        print(f"本国公民均值: {lux.mean():.2f} (n={len(lux)})")
        print(f"外国公民均值: {foreign.mean():.2f} (n={len(foreign)})")
        print(f"T统计量: {t_stat:.3f}")
        print(f"P值: {p_value:.4f}")
        print(f"显著性: {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'}")

# ============================================================
# 8. 示例回归分析
# ============================================================

print("\n" + "=" * 60)
print("示例回归分析框架")
print("=" * 60)

# 检查可用于回归的变量
print("\n可用于回归分析的变量类型:")
print(f"- 人口统计学: D_SEXE, D_CAT_AGE, D_REVENU, D_OCCUPATION, etc.")
print(f"- 态度变量: M系列 ({len([c for c in all_respondents.columns if c.startswith('M')])} 个)")
print(f"- 政治参与: SP系列 ({len([c for c in all_respondents.columns if c.startswith('SP')])} 个)")

# 示例回归模型框架
regression_example = """
# 示例回归模型 (需要根据具体变量调整)

# 模型1: 基础人口统计学模型
model1 = smf.ols(
    'dependent_var ~ D_SEXE + D_CAT_AGE + D_REVENU + D_OCCUPATION',
    data=all_respondents
).fit(cov_type='HC3')

# 模型2: 加入公民类型
model2 = smf.ols(
    'dependent_var ~ citizen_type + D_SEXE + D_CAT_AGE + D_REVENU',
    data=all_respondents
).fit(cov_type='HC3')

# 模型3: 交互效应
model3 = smf.ols(
    'dependent_var ~ citizen_type * D_CAT_AGE + D_SEXE + D_REVENU',
    data=all_respondents
).fit(cov_type='HC3')

print(model1.summary())
print(model2.summary())
print(model3.summary())
"""

print("\n回归模型示例代码:")
print(regression_example)

# ============================================================
# 9. 数据导出
# ============================================================

print("\n" + "=" * 60)
print("数据导出")
print("=" * 60)

# 导出处理后的数据
panel.to_csv("panel_data.csv", index=False)
all_respondents.to_csv("all_respondents.csv", index=False)

print("✅ 已保存:")
print("   - panel_data.csv (选前选后匹配数据)")
print("   - all_respondents.csv (所有受访者数据)")

# ============================================================
# 10. 下一步研究建议
# ============================================================

print("\n" + "=" * 60)
print("下一步研究建议")
print("=" * 60)
import pandas as pd
import numpy as np

print("=" * 80)
print("卢森堡2023选举数据 - 详细变量探索")
print("=" * 80)

# 加载数据
pre = pd.read_stata("pre-electoral-2023-complet.dta", convert_categoricals=False)
post = pd.read_stata("post-electoral-2023.dta", convert_categoricals=False)
post_foreign = pd.read_stata("post-electoral etrangers.dta", convert_categoricals=False)

# ============================================================
# 1. 按变量前缀分类 (PRE-ELECTORAL)
# ============================================================
print("\n" + "=" * 80)
print("PRE-ELECTORAL 数据变量分类")
print("=" * 80)

pre_vars = {}
for col in pre.columns:
    prefix = col.split('_')[0] if '_' in col else col[:2]
    if prefix not in pre_vars:
        pre_vars[prefix] = []
    pre_vars[prefix].append(col)

for prefix in sorted(pre_vars.keys()):
    print(f"\n【{prefix}开头】 ({len(pre_vars[prefix])} 个变量)")
    print(f"  示例: {pre_vars[prefix][:5]}")
    
    # 显示前几个变量的取值情况
    for var in pre_vars[prefix][:3]:
        unique_vals = pre[var].dropna().unique()
        print(f"    {var}: {len(unique_vals)} 个唯一值, 示例={list(unique_vals[:5])}")

# ============================================================
# 2. 按变量前缀分类 (POST-ELECTORAL)
# ============================================================
print("\n" + "=" * 80)
print("POST-ELECTORAL 数据变量分类")
print("=" * 80)

post_vars = {}
for col in post.columns:
    prefix = col.split('_')[0] if '_' in col else col[:2]
    if prefix not in post_vars:
        post_vars[prefix] = []
    post_vars[prefix].append(col)

for prefix in sorted(post_vars.keys()):
    print(f"\n【{prefix}开头】 ({len(post_vars[prefix])} 个变量)")
    print(f"  示例: {post_vars[prefix][:5]}")
    
    # 显示前几个变量的取值情况
    for var in post_vars[prefix][:3]:
        unique_vals = post[var].dropna().unique()
        print(f"    {var}: {len(unique_vals)} 个唯一值, 示例={list(unique_vals[:5])}")

# ============================================================
# 3. 寻找关键变量
# ============================================================
print("\n" + "=" * 80)
print("关键变量识别")
print("=" * 80)

# 投票相关
print("\n【可能的投票变量】")
vote_keywords = ['vote', 'parti', 'party', 'election', 'ballot']
for dataset_name, dataset in [('PRE', pre), ('POST', post)]:
    vote_vars = [col for col in dataset.columns 
                 if any(keyword in col.lower() for keyword in vote_keywords)]
    if vote_vars:
        print(f"\n{dataset_name}数据集:")
        for var in vote_vars[:10]:
            print(f"  - {var}")

# 政治态度
print("\n【可能的政治态度变量】")
attitude_keywords = ['interes', 'satisf', 'trust', 'confian', 'opinion']
for dataset_name, dataset in [('PRE', pre), ('POST', post)]:
    att_vars = [col for col in dataset.columns 
                if any(keyword in col.lower() for keyword in attitude_keywords)]
    if att_vars:
        print(f"\n{dataset_name}数据集:")
        for var in att_vars[:10]:
            print(f"  - {var}")

# ============================================================
# 4. 查看 SP 和 M 变量的具体内容
# ============================================================
print("\n" + "=" * 80)
print("SP 和 M 变量详细信息")
print("=" * 80)

print("\n【PRE数据中的 SP 变量】")
sp_vars_pre = [col for col in pre.columns if col.startswith('SP')]
if sp_vars_pre:
    for var in sp_vars_pre[:10]:
        print(f"\n变量: {var}")
        print(f"  非缺失值: {pre[var].notna().sum()} / {len(pre)}")
        print(f"  取值范围: {pre[var].min()} ~ {pre[var].max()}")
        print(f"  取值分布:")
        print(pre[var].value_counts().head())
else:
    print("  未找到 SP 开头的变量")

print("\n【PRE数据中的 M 变量】")
m_vars_pre = [col for col in pre.columns if col.startswith('M') and len(col) <= 5]
if m_vars_pre:
    for var in m_vars_pre[:10]:
        print(f"\n变量: {var}")
        print(f"  非缺失值: {pre[var].notna().sum()} / {len(pre)}")
        print(f"  取值范围: {pre[var].min()} ~ {pre[var].max()}")
        print(f"  取值分布:")
        print(pre[var].value_counts().head())
else:
    print("  未找到 M 开头的变量")

print("\n【POST数据中的 Q 变量】")
q_vars_post = [col for col in post.columns if col.startswith('Q') and len(col) <= 5]
if q_vars_post:
    for var in q_vars_post[:10]:
        print(f"\n变量: {var}")
        print(f"  非缺失值: {post[var].notna().sum()} / {len(post)}")
        print(f"  取值范围: {post[var].min()} ~ {post[var].max()}")
        print(f"  取值分布:")
        print(post[var].value_counts().head())
else:
    print("  未找到 Q 开头的变量")

# ============================================================
# 5. 人口统计学变量详情
# ============================================================
print("\n" + "=" * 80)
print("人口统计学变量详情")
print("=" * 80)

demo_vars = ['D_SEXE', 'D_CAT_AGE', 'D_NATIO', 'D_REVENU', 'D_OCCUPATION']

for var in demo_vars:
    if var in post.columns:
        print(f"\n【{var}】")
        print(post[var].value_counts().sort_index())

# ============================================================
# 6. 外国公民数据特有变量
# ============================================================
print("\n" + "=" * 80)
print("外国公民数据特有变量")
print("=" * 80)

foreign_only = set(post_foreign.columns) - set(post.columns)
print(f"\n外国公民数据特有变量 ({len(foreign_only)} 个):")
for var in sorted(list(foreign_only))[:20]:
    print(f"  - {var}")

# ============================================================
# 7. 生成变量字典
# ============================================================
print("\n" + "=" * 80)
print("生成变量字典导出")
print("=" * 80)

# 创建变量字典
var_dict = []

for col in pre.columns:
    var_dict.append({
        'variable': col,
        'dataset': 'pre',
        'n_valid': pre[col].notna().sum(),
        'n_unique': pre[col].nunique(),
        'min': pre[col].min() if pre[col].dtype in ['float64', 'int64'] else None,
        'max': pre[col].max() if pre[col].dtype in ['float64', 'int64'] else None
    })

for col in post.columns:
    var_dict.append({
        'variable': col,
        'dataset': 'post',
        'n_valid': post[col].notna().sum(),
        'n_unique': post[col].nunique(),
        'min': post[col].min() if post[col].dtype in ['float64', 'int64'] else None,
        'max': post[col].max() if post[col].dtype in ['float64', 'int64'] else None
    })

var_dict_df = pd.DataFrame(var_dict)
var_dict_df.to_csv('variable_dictionary.csv', index=False)

print("✅ 变量字典已保存到: variable_dictionary.csv")
print("\n你可以用Excel打开这个文件查看所有变量的详细信息!")

print("\n" + "=" * 80)
print("探索完成!")
print("=" * 80)
import pandas as pd
import numpy as np
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

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
post['citizen_type'] = 0  # 本国
post_foreign['citizen_type'] = 1  # 外国
common_vars = list(set(post.columns).intersection(set(post_foreign.columns)))
all_respondents = pd.concat([post[common_vars], post_foreign[common_vars]], ignore_index=True)

print(f"✅ Panel数据: {len(panel)} 观测")
print(f"✅ 所有受访者: {len(all_respondents)} 观测\n")

# ============================================================
# 研究1: 政治兴趣的稳定性 (选前 vs 选后)
# ============================================================
print("\n" + "=" * 80)
print("研究1: 政治兴趣的稳定性")
print("=" * 80)

# SP1 (选前政治兴趣) vs Q1 (选后政治兴趣)
# 注意: 需要重新编码使得分数一致 (SP1越小越感兴趣, Q1也是)

panel['political_interest_pre'] = panel['SP1_pre']
panel['political_interest_post'] = panel['Q1']

# 交叉表
print("\n【选前政治兴趣 vs 选后政治兴趣 交叉表】")
crosstab = pd.crosstab(panel['political_interest_pre'], panel['political_interest_post'])
print(crosstab)

# 相关系数
corr = panel[['political_interest_pre', 'political_interest_post']].corr()
print(f"\n相关系数: {corr.iloc[0,1]:.3f}")

# 配对 t 检验
t_stat, p_value = stats.ttest_rel(
    panel['political_interest_pre'].dropna(), 
    panel['political_interest_post'].dropna()
)
print(f"配对t检验: t={t_stat:.3f}, p={p_value:.4f}")

# 回归分析: 预测选后兴趣
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

# 选择几个关键态度变量进行比较
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

# 回归分析: 控制人口统计学变量后的差异
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

# 创建政治参与指数 (基于多个SP变量)
# SP1: 政治兴趣 (反向编码)
# SP3: 投票意向
# SP11系列: 政党态度

panel['interest_reversed'] = 5 - panel['SP1_pre']  # 反向编码
panel['will_vote'] = (panel['SP3_pre'] == 1).astype(float)  # 是否打算投票

# 计算政党态度的平均分 (SP11_1 到 SP11_12)
sp11_vars = [f'SP11_{i}_pre' for i in range(1, 13)]
available_sp11 = [v for v in sp11_vars if v in panel.columns]
if available_sp11:
    panel['party_engagement'] = panel[available_sp11].mean(axis=1, skipna=True)
else:
    panel['party_engagement'] = np.nan

print("\n【政治参与指标描述】")
print(panel[['interest_reversed', 'will_vote', 'party_engagement']].describe())

# 多元回归: 预测是否打算投票
model3a = smf.logit(
    'will_vote ~ D_SEXE_pre + D_CAT_AGE_pre + D_REVENU_pre + D_OCCUPATION_pre',
    data=panel
).fit()

print("\n【Logistic回归: 预测投票意向】")
print(model3a.summary())

# OLS回归: 预测政治兴趣
model3b = smf.ols(
    'interest_reversed ~ D_SEXE_pre + D_CAT_AGE_pre + D_REVENU_pre + D_OCCUPATION_pre',
    data=panel
).fit(cov_type='HC3')

print("\n【OLS回归: 预测政治兴趣】")
print(model3b.summary())

# ============================================================
# 模型对比表
# ============================================================
print("\n" + "=" * 80)
print("模型对比总结")
print("=" * 80)

# 使用 summary_col 创建对比表
info_dict = {
    'N': lambda x: f"{int(x.nobs)}",
    'R²': lambda x: f"{x.rsquared:.3f}" if hasattr(x, 'rsquared') else 'N/A'
}

comparison = summary_col(
    [model1, model3b],
    stars=True,
    float_format='%.3f',
    model_names=['Model1:选后兴趣', 'Model3:政治兴趣'],
    info_dict=info_dict
)

print(comparison)

# ============================================================
# 导出结果
# ============================================================
print("\n" + "=" * 80)
print("导出结果")
print("=" * 80)

# 导出描述性统计
desc_stats = panel[['political_interest_pre', 'political_interest_post', 
                     'interest_reversed', 'will_vote']].describe()
desc_stats.to_csv('descriptive_statistics.csv')

# 导出本国vs外国对比
results_df.to_csv('citizen_comparison.csv', index=False)

# 导出回归结果摘要
with open('regression_results.txt', 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("模型1: 预测选后政治兴趣\n")
    f.write("=" * 80 + "\n")
    f.write(str(model1.summary()))
    f.write("\n\n")
    
    f.write("=" * 80 + "\n")
    f.write("模型2: M1态度 ~ 公民类型\n")
    f.write("=" * 80 + "\n")
    if 'M1' in all_respondents.columns:
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
print("  - citizen_comparison.csv (本国vs外国对比)")
print("  - regression_results.txt (完整回归结果)")

# ============================================================
# 研究发现总结
# ============================================================
print("\n" + "=" * 80)
print("研究发现总结")
print("=" * 80)

summary_text = f"""
【研究1: 政治兴趣稳定性】
- 选前选后政治兴趣相关系数: {corr.iloc[0,1]:.3f}
- 配对t检验 p值: {p_value:.4f}
- 解读: {'政治兴趣在选举前后显著变化' if p_value < 0.05 else '政治兴趣相对稳定'}

【研究2: 本国vs外国公民】
- 在 {len([r for r in results if r['Significant'] != 'ns'])} 个态度变量上存在显著差异
- 最大差异变量: {results_df.loc[results_df['Difference'].abs().idxmax(), 'Variable']}

【研究3: 人口统计学影响】
- 年龄对政治兴趣的影响: {'显著' if model3b.pvalues.get('D_CAT_AGE_pre', 1) < 0.05 else '不显著'}
- 性别对政治兴趣的影响: {'显著' if model3b.pvalues.get('D_SEXE_pre', 1) < 0.05 else '不显著'}

建议:
1. 根据变量的具体含义(需要codebook)进一步解释结果
2. 考虑增加中介效应或调节效应分析
3. 可视化关键发现(需要matplotlib)
"""

print(summary_text)

with open('research_summary.txt', 'w', encoding='utf-8') as f:
    f.write(summary_text)

print("✅ 已保存: research_summary.txt")

print("\n" + "=" * 80)
print("分析完成! 🎉")
print("=" * 80)