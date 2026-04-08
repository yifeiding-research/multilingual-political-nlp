import json
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # TkAgg backend for VS Code support
import numpy as np
from datetime import datetime
import os

# Set English font
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def load_data(filename='political_transition_analysis.json'):
    """Load analysis data"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return []

def create_overview_chart(data):
    """Create overview charts"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('YouTube Political Content Shift Analysis - Overview', fontsize=16, fontweight='bold')
    
    # 1. Conversion Score Distribution
    scores = [d['conversion_score'] for d in data[:20]]
    names = [d['channel_name'][:20] for d in data[:20]]
    colors = ['#d62728' if s >= 70 else '#ff7f0e' if s >= 40 else '#2ca02c' for s in scores]
    
    axes[0, 0].barh(names, scores, color=colors)
    axes[0, 0].set_xlabel('Conversion Score', fontweight='bold')
    axes[0, 0].set_title('Top 20 Channels by Conversion Score', fontweight='bold')
    axes[0, 0].set_xlim(0, 110)
    axes[0, 0].invert_yaxis()
    
    # 2. Country Distribution
    countries = {}
    for d in data:
        country = d['country']
        countries[country] = countries.get(country, 0) + 1
    
    country_map = {'FR': 'France', 'HU': 'Hungary', 'LU': 'Luxembourg'}
    country_names = [country_map.get(k, k) for k in countries.keys()]
    country_counts = list(countries.values())
    colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    axes[0, 1].pie(country_counts, labels=country_names, autopct='%1.1f%%', 
                   colors=colors_pie, startangle=90)
    axes[0, 1].set_title('Channel Distribution by Country', fontweight='bold')
    
    # 3. Early vs Recent Political Content
    top_10 = data[:10]
    x = np.arange(len(top_10))
    width = 0.35
    
    early = [d['early_period_political_avg']*100 for d in top_10]
    recent = [d['recent_period_political_avg']*100 for d in top_10]
    names_short = [d['channel_name'][:15] for d in top_10]
    
    axes[1, 0].bar(x - width/2, early, width, label='Early Period', color='#90EE90')
    axes[1, 0].bar(x + width/2, recent, width, label='Recent Period', color='#FF6B6B')
    axes[1, 0].set_ylabel('Political Content Probability (%)', fontweight='bold')
    axes[1, 0].set_title('Early vs Recent Political Content Comparison', fontweight='bold')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(names_short, rotation=45, ha='right', fontsize=8)
    axes[1, 0].legend()
    axes[1, 0].set_ylim(0, 100)
    
    # 4. Shift Strength Classification
    strengths = {}
    for d in data[:20]:
        strength = d['shift_strength']
        strengths[strength] = strengths.get(strength, 0) + 1
    
    strength_names = list(strengths.keys())
    strength_counts = list(strengths.values())
    colors_strength = ['#d62728', '#ff7f0e', '#2ca02c']
    
    axes[1, 1].bar(strength_names, strength_counts, color=colors_strength)
    axes[1, 1].set_ylabel('Number of Channels', fontweight='bold')
    axes[1, 1].set_title('Shift Strength Classification (Top 20)', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('report_overview_en.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: report_overview_en.png")
    plt.show()

def create_top_channels_detail(data, top_n=5):
    """Create detailed comparison for top channels"""
    top_channels = data[:top_n]
    
    fig, axes = plt.subplots(1, top_n, figsize=(16, 5))
    if top_n == 1:
        axes = [axes]
    
    fig.suptitle(f'Top {top_n} Political Shift Channels - Detailed Comparison', fontsize=14, fontweight='bold')
    
    for idx, channel in enumerate(top_channels):
        early = channel['early_period_political_avg']
        recent = channel['recent_period_political_avg']
        trend = channel['overall_trend']
        
        # Create mini chart
        ax = axes[idx]
        categories = ['Early', 'Recent']
        values = [early*100, recent*100]
        
        bars = ax.bar(categories, values, color=['#90EE90', '#FF6B6B'], width=0.5)
        ax.set_ylim(0, 100)
        ax.set_ylabel('Political Probability (%)', fontweight='bold', fontsize=9)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Title with channel name and score
        title = f"{channel['channel_name'][:15]}\nScore: {channel['conversion_score']}/100"
        ax.set_title(title, fontweight='bold', fontsize=10)
        
        # Add trend arrow
        ax.text(0.5, 105, f"Trend: {trend:+.1%}", 
               ha='center', fontsize=10, fontweight='bold',
               color='red' if trend > 0 else 'green')
    
    plt.tight_layout()
    plt.savefig('report_top_channels_en.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: report_top_channels_en.png")
    plt.show()

def create_scatter_plot(data):
    """Create scatter plot: Early vs Trend"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    top_20 = data[:20]
    early = [d['early_period_political_avg']*100 for d in top_20]
    trend = [d['overall_trend']*100 for d in top_20]
    scores = [d['conversion_score'] for d in top_20]
    names = [d['channel_name'] for d in top_20]
    
    # Color by country
    colors_map = {'FR': '#FF6B6B', 'HU': '#4ECDC4', 'LU': '#45B7D1'}
    colors = [colors_map.get(d['country'], '#999999') for d in top_20]
    
    scatter = ax.scatter(early, trend, s=[s*5 for s in scores], 
                        c=colors, alpha=0.6, edgecolors='black', linewidth=1)
    
    # Add labels
    for i, name in enumerate(names):
        ax.annotate(name[:12], (early[i], trend[i]), 
                   fontsize=8, ha='center', va='center')
    
    ax.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.3)
    ax.axvline(x=35, color='gray', linestyle='--', linewidth=1, alpha=0.3)
    
    ax.set_xlabel('Early Period Political Content (%)', fontweight='bold', fontsize=12)
    ax.set_ylabel('Political Content Shift Trend (%)', fontweight='bold', fontsize=12)
    ax.set_title('Political Shift Scatter Plot: Early Content vs Trend\n(Bubble size = Conversion Score)', 
                fontweight='bold', fontsize=13)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#FF6B6B', label='France (FR)'),
                      Patch(facecolor='#4ECDC4', label='Hungary (HU)'),
                      Patch(facecolor='#45B7D1', label='Luxembourg (LU)')]
    ax.legend(handles=legend_elements, loc='upper left')
    
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('report_scatter_en.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: report_scatter_en.png")
    plt.show()

def create_html_report(data):
    """Create HTML report"""
    # Statistics
    total_channels = len(data)
    significant = len([d for d in data if d['conversion_score'] >= 30])
    avg_trend = np.mean([d['overall_trend']*100 for d in data]) if data else 0
    
    # Generate table rows
    rows = ""
    for i, channel in enumerate(data[:20], 1):
        trend_symbol = "↑" if channel['overall_trend'] > 0 else "↓"
        trend_class = "trend-positive" if channel['overall_trend'] > 0 else "trend-negative"
        country_class = f"country-{channel['country'].lower()}"
        
        country_map = {'FR': 'France', 'HU': 'Hungary', 'LU': 'Luxembourg'}
        country_display = country_map.get(channel['country'], channel['country'])
        
        row = f"""
        <tr>
            <td class="rank">#{i}</td>
            <td><strong>{channel['channel_name']}</strong></td>
            <td><span class="country-badge {country_class}">{country_display}</span></td>
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
    
    # Use f-string with double braces for CSS
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>YouTube Political Shift Analysis Report</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
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
            <h1>🎬 YouTube Political Content Shift Analysis Report</h1>
            <div class="subtitle">Machine Learning Analysis using TF-IDF + Naive Bayes Classifier</div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_channels}</div>
                    <div class="stat-label">Total Channels Analyzed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{significant}</div>
                    <div class="stat-label">Significant Shift Channels</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_trend:.1f}%</div>
                    <div class="stat-label">Average Shift Magnitude</div>
                </div>
            </div>
            
            <h2>Top 20 Political Shift Channels Ranking</h2>
            <table class="channel-table">
                <tr>
                    <th>Rank</th>
                    <th>Channel Name</th>
                    <th>Country</th>
                    <th>Conversion Score</th>
                    <th>Early Political %</th>
                    <th>Recent Political %</th>
                    <th>Trend Change</th>
                    <th>Shift Strength</th>
                </tr>
                {rows}
            </table>
        </div>
    </body>
    </html>
    """
    
    with open('report_en.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Saved: report_en.html (Open in browser)")

def create_summary_txt(data):
    """Create text summary report"""
    summary = "=" * 80 + "\n"
    summary += "YouTube Political Content Shift Analysis - Final Report\n"
    summary += "=" * 80 + "\n\n"
    
    summary += "📊 Overall Statistics\n"
    summary += "-" * 80 + "\n"
    summary += f"Total Channels Analyzed: {len(data)}\n"
    summary += f"Significant Shift Channels (Score ≥ 30): {len([d for d in data if d['conversion_score'] >= 30])}\n"
    summary += f"Average Shift Magnitude: {np.mean([d['overall_trend']*100 for d in data]):.2f}%\n"
    summary += f"Strongest Shift Channel: {data[0]['channel_name']} (Score: {data[0]['conversion_score']}/100)\n\n"
    
    summary += "🏆 Top 10 Channels - Detailed Information\n"
    summary += "-" * 80 + "\n"
    
    country_map = {'FR': 'France', 'HU': 'Hungary', 'LU': 'Luxembourg'}
    
    for i, channel in enumerate(data[:10], 1):
        country_display = country_map.get(channel['country'], channel['country'])
        summary += f"\n#{i}. {channel['channel_name']} ({country_display})\n"
        summary += f"   Conversion Score: {channel['conversion_score']}/100\n"
        summary += f"   Early Period Political Content: {channel['early_period_political_avg']:.1%}\n"
        summary += f"   Recent Period Political Content: {channel['recent_period_political_avg']:.1%}\n"
        summary += f"   Overall Trend Change: {channel['overall_trend']:+.1%}\n"
        summary += f"   Shift Strength: {channel['shift_strength']}\n"
        summary += f"   Total Videos Analyzed: {channel['total_videos_analyzed']}\n"
        if channel['has_transition']:
            summary += f"   ⚡ Transition Point Detected: {channel['transition_date']}\n"
    
    summary += "\n" + "=" * 80 + "\n"
    summary += "Methodology:\n"
    summary += "-" * 80 + "\n"
    summary += "This analysis uses machine learning to detect political content shifts:\n"
    summary += "- TF-IDF Vectorizer: Extracts features from video titles and descriptions\n"
    summary += "- Naive Bayes Classifier: Predicts political content probability\n"
    summary += "- Conversion Score: Rates shift strength from 0-100 points\n"
    summary += "- Transition Detection: Identifies inflection points in content evolution\n\n"
    summary += "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    summary += "=" * 80 + "\n"
    
    with open('report_summary_en.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    print("✓ Saved: report_summary_en.txt")
    print(summary)

if __name__ == "__main__":
    print("Loading data...")
    data = load_data()
    
    if not data:
        print("No data available for analysis")
        exit()
    
    print(f"Loaded data for {len(data)} channels\n")
    
    print("Generating visualization reports...\n")
    print("1️⃣  Generating overview charts...")
    create_overview_chart(data)
    
    print("\n2️⃣  Generating top channels comparison...")
    create_top_channels_detail(data, top_n=5)
    
    print("\n3️⃣  Generating scatter plot...")
    create_scatter_plot(data)
    
    print("\n4️⃣  Generating HTML report...")
    create_html_report(data)
    
    print("\n5️⃣  Generating text summary...")
    create_summary_txt(data)
    
    print("\n" + "=" * 80)
    print("✅ All reports generated successfully!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  📊 report_overview_en.png      - Overview charts")
    print("  📊 report_top_channels_en.png  - Top channels comparison")
    print("  📊 report_scatter_en.png       - Scatter analysis")
    print("  🌐 report_en.html              - Interactive HTML report")
    print("  📄 report_summary_en.txt       - Text summary")
    print("\nTip: Open report_en.html in your browser for detailed data tables")
    print("=" * 80)