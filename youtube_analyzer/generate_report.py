import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # 使用TkAgg后端，支持VS Code
import numpy as np
from datetime import datetime
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_data(filename='political_transition_analysis.json'):
    """加载分析数据"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到 {filename}")
        return []

def create_overview_chart(data):
    """创建概览图表"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('YouTube政治转变频道 - 总体概览', fontsize=16, fontweight='bold')
    
    # 1. 转变评分分布
    scores = [d['conversion_score'] for d in data[:20]]
    names = [d['channel_name'][:20] for d in data[:20]]
    colors = ['#d62728' if s >= 70 else '#ff7f0e' if s >= 40 else '#2ca02c' for s in scores]
    
    axes[0, 0].barh(names, scores, color=colors)
    axes[0, 0].set_xlabel('转变评分', fontweight='bold')
    axes[0, 0].set_title('Top 20频道转变评分', fontweight='bold')
    axes[0, 0].set_xlim(0, 110)
    axes[0, 0].invert_yaxis()
    
    # 2. 国家分布
    countries = {}
    for d in data:
        country = d['country']
        countries[country] = countries.get(country, 0) + 1
    
    country_names = list(countries.keys())
    country_counts = list(countries.values())
    colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    axes[0, 1].pie(country_counts, labels=country_names, autopct='%1.1f%%', 
                   colors=colors_pie, startangle=90)
    axes[0, 1].set_title('频道国家分布', fontweight='bold')
    
    # 3. 早期vs最近政治概率
    top_10 = data[:10]
    x = np.arange(len(top_10))
    width = 0.35
    
    early = [d['early_period_political_avg']*100 for d in top_10]
    recent = [d['recent_period_political_avg']*100 for d in top_10]
    names_short = [d['channel_name'][:15] for d in top_10]
    
    axes[1, 0].bar(x - width/2, early, width, label='早期', color='#90EE90')
    axes[1, 0].bar(x + width/2, recent, width, label='最近', color='#FF6B6B')
    axes[1, 0].set_ylabel('政治内容概率 (%)', fontweight='bold')
    axes[1, 0].set_title('早期 vs 最近政治内容对比', fontweight='bold')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(names_short, rotation=45, ha='right', fontsize=8)
    axes[1, 0].legend()
    axes[1, 0].set_ylim(0, 100)
    
    # 4. 转变强度分类
    strengths = {}
    for d in data[:20]:
        strength = d['shift_strength']
        strengths[strength] = strengths.get(strength, 0) + 1
    
    strength_names = list(strengths.keys())
    strength_counts = list(strengths.values())
    colors_strength = ['#d62728', '#ff7f0e', '#2ca02c']
    
    axes[1, 1].bar(strength_names, strength_counts, color=colors_strength)
    axes[1, 1].set_ylabel('频道数', fontweight='bold')
    axes[1, 1].set_title('转变强度分类 (Top 20)', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('report_overview.png', dpi=300, bbox_inches='tight')
    print("✓ 已保存: report_overview.png")
    plt.show()

def create_top_channels_detail(data, top_n=5):
    """创建Top频道详细对比图"""
    top_channels = data[:top_n]
    
    fig, axes = plt.subplots(1, top_n, figsize=(16, 5))
    if top_n == 1:
        axes = [axes]
    
    fig.suptitle(f'Top {top_n}政治转变频道 - 详细对比', fontsize=14, fontweight='bold')
    
    for idx, channel in enumerate(top_channels):
        early = channel['early_period_political_avg']
        recent = channel['recent_period_political_avg']
        trend = channel['overall_trend']
        
        # 创建迷你图表
        ax = axes[idx]
        categories = ['早期', '最近']
        values = [early*100, recent*100]
        
        bars = ax.bar(categories, values, color=['#90EE90', '#FF6B6B'], width=0.5)
        ax.set_ylim(0, 100)
        ax.set_ylabel('政治概率 (%)', fontweight='bold', fontsize=9)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # 标题包含频道名和评分
        title = f"{channel['channel_name'][:15]}\n评分: {channel['conversion_score']}/100"
        ax.set_title(title, fontweight='bold', fontsize=10)
        
        # 添加趋势箭头
        ax.text(0.5, 105, f"趋势: {trend:+.1%}", 
               ha='center', fontsize=10, fontweight='bold',
               color='red' if trend > 0 else 'green')
    
    plt.tight_layout()
    plt.savefig('report_top_channels.png', dpi=300, bbox_inches='tight')
    print(f"✓ 已保存: report_top_channels.png")
    plt.show()

def create_scatter_plot(data):
    """创建散点图：早期vs趋势"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_20 = data[:20]
    early = [d['early_period_political_avg']*100 for d in top_20]
    trend = [d['overall_trend']*100 for d in top_20]
    scores = [d['conversion_score'] for d in top_20]
    names = [d['channel_name'] for d in top_20]
    
    # 按国家着色
    colors_map = {'FR': '#FF6B6B', 'HU': '#4ECDC4', 'LU': '#45B7D1'}
    colors = [colors_map.get(d['country'], '#999999') for d in top_20]
    
    scatter = ax.scatter(early, trend, s=[s*5 for s in scores], 
                        c=colors, alpha=0.6, edgecolors='black', linewidth=1)
    
    # 添加标签
    for i, name in enumerate(names):
        ax.annotate(name[:12], (early[i], trend[i]), 
                   fontsize=8, ha='center', va='center')
    
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
    ax.axvline(x=35, color='gray', linestyle='--', linewidth=1, alpha=0.3)
    
    ax.set_xlabel('早期政治内容概率 (%)', fontweight='bold', fontsize=12)
    ax.set_ylabel('政治内容变化趋势 (%)', fontweight='bold', fontsize=12)
    ax.set_title('政治转变散点图：早期内容 vs 转变趋势\n(气泡大小=转变评分)', 
                fontweight='bold', fontsize=13)
    
    # 添加图例
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#FF6B6B', label='法国 (FR)'),
                      Patch(facecolor='#4ECDC4', label='匈牙利 (HU)'),
                      Patch(facecolor='#45B7D1', label='卢森堡 (LU)')]
    ax.legend(handles=legend_elements, loc='upper left')
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('report_scatter.png', dpi=300, bbox_inches='tight')
    print("✓ 已保存: report_scatter.png")
    plt.show()

def create_html_report(data):
    """创建HTML报告"""
    # 统计数据
    total_channels = len(data)
    significant = len([d for d in data if d['conversion_score'] >= 30])
    avg_trend = np.mean([d['overall_trend']*100 for d in data]) if data else 0
    
    # 生成表格行
    rows = ""
    for i, channel in enumerate(data[:20], 1):
        trend_symbol = "↑" if channel['overall_trend'] > 0 else "↓"
        trend_class = "trend-positive" if channel['overall_trend'] > 0 else "trend-negative"
        country_class = f"country-{channel['country'].lower()}"
        
        row = f"""
        <tr>
            <td class="rank">#{i}</td>
            <td><strong>{channel['channel_name']}</strong></td>
            <td><span class="country-badge {country_class}">{channel['country']}</span></td>
            <td>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div class="score-bar" style="width: 80px;">
                        <div class="score-text">{channel['conversion_score']}/100</div>
                    </div>
                </div>
            </td>
            <td>{channel['early_period_political_avg']:.1%}</td>
            <td>{channel['recent_period_political_avg']:.1%}</td>
            <td class="{trend_class}">{trend_symbol} {channel['overall_trend']:+.1%}</td>
            <td>{channel['shift_strength']}</td>
        </tr>
        """
        rows += row
    
    # 使用字符串拼接而不是format()
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>YouTube政治转变频道分析报告</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); }}
            h1 {{ color: #333; margin-bottom: 10px; text-align: center; }}
            .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 40px; }}
            .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 32px; font-weight: bold; }}
            .stat-label {{ font-size: 12px; margin-top: 10px; opacity: 0.9; }}
            .channel-table {{ width: 100%; border-collapse: collapse; margin-bottom: 40px; }}
            .channel-table th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            .channel-table td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
            .channel-table tr:hover {{ background: #f5f5f5; }}
            .rank {{ font-weight: bold; color: #667eea; }}
            .score-bar {{ background: linear-gradient(90deg, #90EE90, #FF6B6B); height: 20px; border-radius: 4px; }}
            .score-text {{ color: white; font-size: 12px; padding: 2px 6px; font-weight: bold; }}
            .trend-positive {{ color: #d62728; font-weight: bold; }}
            .trend-negative {{ color: #2ca02c; font-weight: bold; }}
            .country-badge {{ display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; color: white; }}
            .country-fr {{ background: #FF6B6B; }}
            .country-hu {{ background: #4ECDC4; }}
            .country-lu {{ background: #45B7D1; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 YouTube政治转变频道分析报告</h1>
            <div class="subtitle">基于TF-IDF + 朴素贝叶斯机器学习模型分析</div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_channels}</div>
                    <div class="stat-label">总分析频道数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{significant}</div>
                    <div class="stat-label">显著转变频道</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_trend:.1f}%</div>
                    <div class="stat-label">平均转变幅度</div>
                </div>
            </div>
            
            <h2>Top 20 政治转变频道排行</h2>
            <table class="channel-table">
                <tr>
                    <th>排名</th>
                    <th>频道名称</th>
                    <th>国家</th>
                    <th>转变评分</th>
                    <th>早期政治%</th>
                    <th>最近政治%</th>
                    <th>变化趋势</th>
                    <th>转变强度</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """
    
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ 已保存: report.html (用浏览器打开查看)")

def create_summary_txt(data):
    """创建文本总结报告"""
    summary = "=" * 80 + "\n"
    summary += "YouTube 政治转变频道分析 - 最终报告\n"
    summary += "=" * 80 + "\n\n"
    
    summary += "📊 总体统计\n"
    summary += "-" * 80 + "\n"
    summary += f"总分析频道数: {len(data)}\n"
    summary += f"显著转变频道(评分≥30): {len([d for d in data if d['conversion_score'] >= 30])}\n"
    summary += f"平均转变幅度: {np.mean([d['overall_trend']*100 for d in data]):.2f}%\n"
    summary += f"最强转变频道: {data[0]['channel_name']} (评分: {data[0]['conversion_score']}/100)\n\n"
    
    summary += "🏆 Top 10 频道详细信息\n"
    summary += "-" * 80 + "\n"
    
    for i, channel in enumerate(data[:10], 1):
        summary += f"\n#{i}. {channel['channel_name']} ({channel['country']})\n"
        summary += f"   转变评分: {channel['conversion_score']}/100\n"
        summary += f"   早期政治内容: {channel['early_period_political_avg']:.1%}\n"
        summary += f"   最近政治内容: {channel['recent_period_political_avg']:.1%}\n"
        summary += f"   变化趋势: {channel['overall_trend']:+.1%}\n"
        summary += f"   转变强度: {channel['shift_strength']}\n"
        if channel['has_transition']:
            summary += f"   ⚡ 转折点: {channel['transition_date']}\n"
    
    summary += "\n" + "=" * 80 + "\n"
    summary += "生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    summary += "=" * 80 + "\n"
    
    with open('report_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    print("✓ 已保存: report_summary.txt")
    print(summary)

if __name__ == "__main__":
    print("正在加载数据...")
    data = load_data()
    
    if not data:
        print("没有数据可分析")
        exit()
    
    print(f"已加载 {len(data)} 个频道的数据\n")
    
    print("生成可视化报告...")
    print("\n1️⃣  生成概览图表...")
    create_overview_chart(data)
    
    print("\n2️⃣  生成Top频道对比...")
    create_top_channels_detail(data, top_n=5)
    
    print("\n3️⃣  生成散点图...")
    create_scatter_plot(data)
    
    print("\n4️⃣  生成HTML报告...")
    create_html_report(data)
    
    print("\n5️⃣  生成文本总结...")
    create_summary_txt(data)
    
    print("\n" + "=" * 80)
    print("✅ 所有报告已生成完毕！")
    print("=" * 80)
    print("\n生成的文件:")
    print("  📊 report_overview.png      - 总体概览图表")
    print("  📊 report_top_channels.png  - Top频道对比")
    print("  📊 report_scatter.png       - 散点分析图")
    print("  🌐 report.html              - HTML互动报告")
    print("  📄 report_summary.txt       - 文本总结")
    print("\n提示: 用浏览器打开 report.html 查看详细数据表")
    print("=" * 80)