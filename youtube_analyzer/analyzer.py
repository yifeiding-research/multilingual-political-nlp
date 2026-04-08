import os
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import warnings
warnings.filterwarnings('ignore')

# YouTube API设置
YOUTUBE_API_KEY = "REMOVED"

# 强政治信号关键词（多语言）- 专注于确实的政治内容
POLITICAL_KEYWORDS = {
    'FR': ['macron', 'élysée', 'assemblée nationale', 'senat', 'ministre', 'gouvernement',
           'élection présidentielle', 'vote', 'campaagne électorale', 'partis politiques',
           'marine le pen', 'édouard philippe', 'françois hollande', 'nicolas sarkozy',
           'brexit', 'sanctions', 'union européenne', 'géopolitique', 'diplomatie',
           'réforme des retraites', 'loi travail', 'immigration', 'sécurité', 'terrorisme'],
    'HU': ['orbán', 'fidesz', 'jobbik', 'mszp', 'dk', 'magyar nemzeti',
           'választások 2022', 'választások 2026', 'kúria', 'jogtollást',
           'brüsszel', 'eu szankció', 'uniós pénz', 'померш', 'covid törvény',
           'lezárás intézkedés', 'nemzeti konzultáció', 'védelmi intézkedések'],
    'LU': ['luxembourg', 'xavier bettel', 'ady', 'adl', 'csv', 'spuerkeess',
           'eu parliament', 'luxembourg parliament', 'wahlkampf', 'europawahl',
           'brexit', 'luxemburgische wahl', 'regierungswechsel', 'europäische fragen']
}

# 非政治内容关键词
NON_POLITICAL_KEYWORDS = {
    'FR': ['musique', 'chanson', 'gaming', 'jeu vidéo', 'playthrough', 'comédie', 'sketch',
           'beauté', 'maquillage', 'tutoriel maquillage', 'mode', 'vlog', 'vlog du jour',
           'recette', 'cuisine', 'sport', 'entraînement', 'fitness', 'gym', 'yoga',
           'tutoriel', 'diy', 'craft', 'asmr', 'mukbang', 'réaction', 'critique film',
           'film review', 'gaming tournament', 'esports', 'streaming', 'let play'],
    'HU': ['zene', 'dal', 'videóklip', 'játék', 'gameplay', 'playthrough', 'komédia', 'sketch',
           'szépség', 'sminkelés', 'divat', 'vlog', 'napi vlog', 'recept', 'főzés',
           'sport', 'edzés', 'fitness', 'jóga', 'tanítóvideo', 'diy', 'kézművesség',
           'asmr', 'mukbang', 'react', 'filmkritika', 'videojáték turnir', 'stream'],
    'LU': ['musik', 'lied', 'videoclip', 'spiel', 'gameplay', 'komödie', 'sketch',
           'schönheit', 'make-up', 'mode', 'vlog', 'alltags vlog', 'rezept', 'kochen',
           'sport', 'training', 'fitness', 'yoga', 'tutorial', 'diy', 'handwerk',
           'asmr', 'musikfestival', 'filmkritik', 'gaming tournament', 'stream']
}

class AdvancedYouTubeAnalyzer:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.ml_models = {}
    
    def search_channels(self, query, country_code, max_results=50):
        """搜索YouTube频道"""
        try:
            request = self.youtube.search().list(
                q=query,
                type='channel',
                part='snippet',
                maxResults=min(max_results, 50),
                order='viewCount'
            )
            response = request.execute()
            return response.get('items', [])
        except Exception as e:
            print(f"搜索出错: {e}")
            return []
    
    def get_channel_stats(self, channel_id):
        """获取频道统计数据"""
        try:
            request = self.youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=channel_id
            )
            response = request.execute()
            if response['items']:
                return response['items'][0]
            return None
        except Exception as e:
            print(f"获取频道信息出错: {e}")
            return None
    
    def get_all_videos(self, channel_id, max_results=200):
        """获取频道所有视频（按时间顺序）"""
        try:
            channel_info = self.get_channel_stats(channel_id)
            if not channel_info:
                return []
            
            upload_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
            items = []
            next_page_token = None
            
            while len(items) < max_results:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=upload_playlist_id,
                    maxResults=min(max_results - len(items), 50),
                    pageToken=next_page_token
                )
                response = request.execute()
                items.extend(response.get('items', []))
                next_page_token = response.get('nextPageToken')
                
                if not next_page_token:
                    break
            
            return items
        except Exception as e:
            print(f"获取视频列表出错: {e}")
            return []
    
    def train_political_classifier(self, country_code):
        """训练政治内容分类器 - 精准版"""
        political_texts = POLITICAL_KEYWORDS.get(country_code, [])
        non_political_texts = NON_POLITICAL_KEYWORDS.get(country_code, [])
        
        # 创建高质量的训练样本
        political_samples = []
        for kw in political_texts:
            political_samples.extend([
                kw,
                f"{kw}",
                f"about {kw}",
                f"discussion about {kw}",
            ])
        
        non_political_samples = []
        for kw in non_political_texts:
            non_political_samples.extend([
                kw,
                f"{kw}",
                f"best {kw}",
                f"how to {kw}",
            ])
        
        X = political_samples + non_political_samples
        y = [1] * len(political_samples) + [0] * len(non_political_samples)
        
        # 使用更激进的参数
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                lowercase=True,
                max_features=300,
                ngram_range=(1, 2),
                min_df=1,
                max_df=1.0,
                token_pattern=r'\b\w+\b'  # 更好的分词
            )),
            ('classifier', MultinomialNB(alpha=0.5))  # 增加alpha以提高精度
        ])
        
        pipeline.fit(X, y)
        self.ml_models[country_code] = pipeline
        return pipeline
    
    def predict_political_probability(self, text, country_code):
        """预测文本是政治内容的概率"""
        if country_code not in self.ml_models:
            self.train_political_classifier(country_code)
        
        model = self.ml_models[country_code]
        prob = model.predict_proba([text])[0][1]  # 政治类别的概率
        return prob
    
    def analyze_content_timeline(self, videos, country_code):
        """分析内容随时间的演变"""
        if not videos:
            return None
        
        # 按时间排序（最新的在前）
        videos_sorted = sorted(
            videos,
            key=lambda x: x['snippet']['publishedAt'],
            reverse=True
        )
        
        timeline_data = []
        for video in videos_sorted:
            title = video['snippet']['title']
            description = video['snippet']['description']
            published_at = video['snippet']['publishedAt']
            
            # 合并标题和描述
            text = f"{title} {description}"
            
            # 获取政治概率
            political_prob = self.predict_political_probability(text, country_code)
            
            timeline_data.append({
                'date': published_at,
                'title': title,
                'political_probability': political_prob
            })
        
        return timeline_data
    
    def detect_transition_point(self, timeline_data):
        """检测从非政治到政治的转折点"""
        if len(timeline_data) < 10:
            return None
        
        # 获取政治概率序列
        probs = [item['political_probability'] for item in timeline_data]
        
        # 计算移动平均（平滑数据）
        window = min(5, len(probs) // 4)
        moving_avg = []
        for i in range(len(probs) - window + 1):
            avg = np.mean(probs[i:i+window])
            moving_avg.append(avg)
        
        if len(moving_avg) < 2:
            return None
        
        # 检测变化最大的点（从低到高）
        changes = [moving_avg[i+1] - moving_avg[i] for i in range(len(moving_avg)-1)]
        
        if not changes:
            return None
        
        max_change_idx = np.argmax(changes)
        max_change = changes[max_change_idx]
        
        # 降低阈值到0.15，更容易检测转折
        if max_change > 0.15:
            transition_idx = max_change_idx + window // 2
            if transition_idx < len(timeline_data):
                return {
                    'transition_date': timeline_data[transition_idx]['date'],
                    'transition_strength': float(max_change),
                    'transition_video_index': transition_idx
                }
        
        return None
    
    def calculate_content_shift_metrics(self, timeline_data):
        """计算内容转变指标"""
        if len(timeline_data) < 20:
            return None
        
        # 分成早期和最近两个阶段
        mid_point = len(timeline_data) // 2
        early_period = timeline_data[mid_point:]
        recent_period = timeline_data[:mid_point]
        
        early_avg = np.mean([item['political_probability'] for item in early_period])
        recent_avg = np.mean([item['political_probability'] for item in recent_period])
        
        # 计算标准差（波动性）
        early_std = np.std([item['political_probability'] for item in early_period])
        recent_std = np.std([item['political_probability'] for item in recent_period])
        
        # 计算变化趋势
        trend = recent_avg - early_avg
        
        return {
            'early_period_avg': float(early_avg),
            'recent_period_avg': float(recent_avg),
            'trend': float(trend),
            'early_volatility': float(early_std),
            'recent_volatility': float(recent_std),
            'shift_strength': 'Strong' if abs(trend) > 0.3 else 'Moderate' if abs(trend) > 0.15 else 'Weak'
        }
    
    def is_original_political_channel(self, timeline):
        """判断频道是否从一开始就是政治频道（排除这类频道）"""
        if len(timeline) < 20:
            return False
        
        # 获取最早的视频（在列表末尾）
        earliest_videos = timeline[-10:]
        earliest_avg = np.mean([item['political_probability'] for item in earliest_videos])
        
        # 如果最早的视频就高度政治化（>0.7），说明从一开始就是政治频道
        if earliest_avg > 0.7:
            return True
        return False
    
    def generate_detailed_report(self, channel_id, channel_name, country_code):
        """生成详细分析报告"""
        try:
            print(f"    获取视频数据... {channel_name}")
            videos = self.get_all_videos(channel_id, max_results=200)
            
            if len(videos) < 20:
                print(f"    视频过少，跳过")
                return None
            
            print(f"    分析内容演变... ({len(videos)} 个视频)")
            
            # 分析时间线
            timeline = self.analyze_content_timeline(videos, country_code)
            
            # 过滤：排除从一开始就是政治频道的
            if self.is_original_political_channel(timeline):
                print(f"    （原始政治频道，跳过）")
                return None
            
            # 检测转折点
            transition = self.detect_transition_point(timeline)
            
            # 计算转变指标
            metrics = self.calculate_content_shift_metrics(timeline)
            
            if not metrics:
                return None
            
            # 计算综合转变评分（更严格的标准）
            conversion_score = 0
            
            # 必须满足的基本条件：早期内容明确不是政治
            if metrics['early_period_avg'] > 0.35:
                # 早期已经很政治化，不符合"后来才开始"的定义
                conversion_score = 0
            else:
                # 评分规则：
                # 1. 明显转变：早期极低 + 最近明显提高
                if metrics['recent_period_avg'] > 0.55:
                    conversion_score += 50
                elif metrics['recent_period_avg'] > 0.45:
                    conversion_score += 30
                elif metrics['recent_period_avg'] > 0.35:
                    conversion_score += 15
                
                # 2. 有明显的转折点
                if transition:
                    conversion_score += 25
                
                # 3. 总趋势明显上升
                if metrics['trend'] > 0.25:
                    conversion_score += 20
                elif metrics['trend'] > 0.15:
                    conversion_score += 10
                
                # 4. 最近内容的一致性
                if metrics['recent_volatility'] < 0.15:
                    conversion_score += 15
                elif metrics['recent_volatility'] < 0.25:
                    conversion_score += 8
            
            return {
                'channel_name': channel_name,
                'channel_id': channel_id,
                'country': country_code,
                'total_videos_analyzed': len(videos),
                'early_period_political_avg': round(metrics['early_period_avg'], 3),
                'recent_period_political_avg': round(metrics['recent_period_avg'], 3),
                'overall_trend': round(metrics['trend'], 3),
                'trend_direction': 'Increasing Political Content' if metrics['trend'] > 0 else 'Decreasing Political Content',
                'shift_strength': metrics['shift_strength'],
                'early_volatility': round(metrics['early_volatility'], 3),
                'recent_volatility': round(metrics['recent_volatility'], 3),
                'has_transition': transition is not None,
                'transition_date': transition['transition_date'] if transition else None,
                'transition_strength': round(transition['transition_strength'], 3) if transition else None,
                'conversion_score': conversion_score,
                'likelihood_of_conversion': 'Very High (100+)' if conversion_score >= 100 else 'High (70-99)' if conversion_score >= 70 else 'Medium (40-69)' if conversion_score >= 40 else 'Low (<40)'
            }
        
        except Exception as e:
            print(f"    分析 {channel_name} 时出错: {e}")
            return None

def main():
    analyzer = AdvancedYouTubeAnalyzer(YOUTUBE_API_KEY)
    
    # 搜索查询 - 多垂直领域的非政治创作者
    search_queries = {
        'FR': ['YouTuber français populaire', 'créateur contenu France',
               'influenceur France', 'vlogger français', 'streamer France',
               'gaming YouTuber France', 'France tech YouTube', 'économie France',
               'business France YouTube', 'entrepreneuriat France', 'startup France',
               'France environnement YouTube', 'écologie France', 'social France',
               'France santé YouTube', 'France éducation', 'France culture',
               'France histoire', 'France science', 'France voyage'],
        'HU': ['Magyar YouTuber népszerű', 'magyar tartalomkészítő', 
               'magyar gamer', 'magyar vlogger', 'magyar streamer',
               'magyar tech YouTube', 'magyar üzlet', 'magyar startup',
               'magyar gazdaság', 'magyar oktatás', 'magyar kapu YouTube',
               'magyar egészség', 'magyar kultúra', 'magyar utazás',
               'magyar tudomány', 'magyar történelem'],
        'LU': ['Luxemburger YouTuber', 'Luxemburg Influencer', 
               'Luxemburg Creator', 'Luxembourg tech', 'Luxembourg business',
               'Luxemburg gaming', 'Luxemburg vlogger', 'Luxemburg entrepreneur',
               'Luxembourg health', 'Luxembourg education', 'Luxembourg culture']
    }
    
    all_reports = []
    
    for country_code, queries in search_queries.items():
        print(f"\n【正在分析 {country_code} 的频道】\n")
        
        # 训练该国的分类器
        analyzer.train_political_classifier(country_code)
        print(f"✓ 已训练 {country_code} 的政治内容分类器\n")
        
        for query in queries:
            print(f"搜索: {query}")
            channels = analyzer.search_channels(query, country_code, max_results=10)
            
            for channel in channels:
                channel_id = channel['id']['channelId']
                channel_name = channel['snippet']['title']
                
                report = analyzer.generate_detailed_report(channel_id, channel_name, country_code)
                
                if report:
                    all_reports.append(report)
                    print(f"✓ 完成: {channel_name}\n")
    
    # 按转变评分排序（最高优先）
    all_reports.sort(key=lambda x: x['conversion_score'], reverse=True)
    
    # 过滤：只保留有意义的转变（评分≥30）
    significant_reports = [r for r in all_reports if r['conversion_score'] >= 30]
    
    # 保存所有结果
    with open('political_transition_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, ensure_ascii=False, indent=2)
    
    # 打印Top转变频道
    print("\n" + "="*80)
    print(f"【内容演变分析 - 识别到 {len(significant_reports)} 个显著转变频道】")
    print("="*80 + "\n")
    
    display_count = min(20, len(significant_reports))
    for i, report in enumerate(significant_reports[:display_count], 1):
        print(f"{i}. {report['channel_name']} ({report['country']})")
        print(f"   转变评分: {report['conversion_score']}/100 ({report['likelihood_of_conversion']})")
        print(f"   总视频数: {report['total_videos_analyzed']}")
        print(f"   早期政治平均概率: {report['early_period_political_avg']:.1%}")
        print(f"   最近政治平均概率: {report['recent_period_political_avg']:.1%}")
        print(f"   变化趋势: {report['overall_trend']:+.1%} ({report['trend_direction']})")
        print(f"   转变强度: {report['shift_strength']}")
        if report['has_transition']:
            print(f"   ⚡ 检测到转折点: {report['transition_date']} (强度: {report['transition_strength']})")
        print()
    
    print(f"\n详细报告已保存到: political_transition_analysis.json")

if __name__ == "__main__":
    print("="*80)
    print("YouTube 内容演变机器学习分析工具")
    print("="*80)
    print("\n使用TF-IDF + 朴素贝叶斯分类器分析频道内容转变")
    print("开始分析... (这可能需要5-10分钟)\n")
    
    main()