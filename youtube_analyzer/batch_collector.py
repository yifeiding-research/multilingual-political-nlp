import json
import time
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

YOUTUBE_API_KEY = "REMOVED"

# 搜索词配置 - 按国家和天数分配
SEARCH_CONFIG = {
    'FR': {
        'day1': ['YouTuber français', 'vlogger français', 'gaming YouTuber France', 
                 'streamer France', 'France tech YouTube', 'business France YouTube'],
        'day2': ['entrepreneuriat France', 'startup France', 'France santé', 
                 'France éducation', 'France culture', 'France histoire'],
        'day1_ext': ['sport YouTuber France', 'fitness France YouTube', 'musique France YouTube',
                     'comédie France', 'France voyage YouTube', 'recette France',
                     'beauty France YouTube', 'mode France YouTube', 'lifestyle France',
                     'France podcast', 'critique film France', 'gaming France']
    },
    'HU': {
        'day3': ['Magyar YouTuber', 'magyar gamer', 'magyar vlogger', 
                 'magyar streamer', 'magyar tech', 'magyar oktatás'],
        'day3_ext': ['magyar sport', 'magyar fitness', 'magyar zene',
                     'magyar humor', 'magyar utazás', 'magyar főzés',
                     'magyar szépség', 'magyar lifestyle', 'magyar podcast',
                     'magyar film', 'magyar történelem', 'magyar kulináris']
    },
    'LU': {
        'day4': ['Luxemburger YouTuber', 'Luxemburg tech', 'Luxembourg business',
                 'Luxemburg gaming', 'Luxembourg culture', 'Luxembourg education'],
        'day4_ext': ['Luxembourg sports', 'Luxembourg music', 'Luxembourg travel',
                     'Luxembourg food', 'Luxembourg lifestyle', 'Luxembourg vlog',
                     'Luxembourg podcast', 'Luxembourg fitness', 'Luxembourg health',
                     'Luxemburg entertainment', 'Luxemburg gamer', 'Luxembourg creator']
    }
}

class BatchCollector:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.quota_used = 0
        self.channels_data = []
        self.session_file = 'batch_collection_session.json'
        self.load_session()
    
    def load_session(self):
        """加载之前的采集进度"""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
                self.channels_data = session.get('channels', [])
                self.quota_used = session.get('quota_used', 0)
                print(f"✓ 已加载之前的采集进度")
                print(f"  已采集频道数: {len(self.channels_data)}")
                print(f"  配额已消耗: {self.quota_used}\n")
        except FileNotFoundError:
            print("开始新的采集会话\n")
    
    def save_session(self):
        """保存采集进度"""
        session = {
            'channels': self.channels_data,
            'quota_used': self.quota_used,
            'last_save': datetime.now().isoformat()
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 进度已保存到 {self.session_file}")
    
    def search_channels(self, query, country_code, max_results=10):
        """搜索频道"""
        try:
            request = self.youtube.search().list(
                q=query,
                type='channel',
                part='snippet',
                maxResults=min(max_results, 50),
                order='viewCount'
            )
            response = request.execute()
            self.quota_used += 100
            return response.get('items', [])
        except Exception as e:
            if '403' in str(e):
                print(f"❌ 配额已用完！")
                return []
            return []
    
    def get_channel_info(self, channel_id):
        """获取频道详细信息"""
        try:
            request = self.youtube.channels().list(
                part='statistics,snippet,contentDetails',
                id=channel_id
            )
            response = request.execute()
            self.quota_used += 1
            
            if response and 'items' in response and response['items']:
                return response['items'][0]
            return None
        except Exception:
            return None
    
    def get_videos_sample(self, channel_id):
        """获取频道的视频样本"""
        try:
            channel_info = self.get_channel_info(channel_id)
            if not channel_info:
                return []
            
            if 'contentDetails' not in channel_info:
                return []
            
            upload_playlist_id = channel_info['contentDetails'].get('relatedPlaylists', {}).get('uploads')
            if not upload_playlist_id:
                return []
            
            request = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=upload_playlist_id,
                maxResults=50
            )
            response = request.execute()
            self.quota_used += 1
            
            items = response.get('items', [])
            
            if 'nextPageToken' in response and len(items) < 100:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=upload_playlist_id,
                    pageToken=response['nextPageToken'],
                    maxResults=50
                )
                response = request.execute()
                self.quota_used += 1
                items.extend(response.get('items', []))
            
            return items
        except Exception:
            return []
    
    def collect_batch(self, day_name, search_queries, country_code, channels_per_query=10):
        """采集一批频道"""
        print(f"\n{'='*80}")
        print(f"【{day_name} - {country_code}】")
        print(f"{'='*80}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"当前配额消耗: {self.quota_used}/10000\n")
        
        channels_added = 0
        unique_channel_ids = set(ch['channel_id'] for ch in self.channels_data)
        
        for query_idx, query in enumerate(search_queries, 1):
            if self.quota_used >= 9900:
                print(f"\n⚠️ 配额即将用完，停止采集")
                print(f"已采集 {channels_added} 个新频道")
                break
            
            print(f"\n搜索 ({query_idx}/{len(search_queries)}): {query}")
            print(f"配额剩余: {10000 - self.quota_used}")
            
            channels = self.search_channels(query, country_code, channels_per_query)
            
            for channel in channels:
                if self.quota_used >= 9900:
                    break
                
                channel_id = channel['id']['channelId']
                channel_name = channel['snippet']['title']
                
                if channel_id in unique_channel_ids:
                    continue
                
                print(f"  处理: {channel_name[:40]}...", end='', flush=True)
                
                channel_info = self.get_channel_info(channel_id)
                if not channel_info:
                    print(" ❌")
                    continue
                
                videos = self.get_videos_sample(channel_id)
                
                if len(videos) < 20:
                    print(" ⏭️ (视频过少)")
                    continue
                
                channel_data = {
                    'channel_id': channel_id,
                    'channel_name': channel_name,
                    'country': country_code,
                    'subscribers': channel_info['statistics'].get('subscriberCount', 0),
                    'view_count': channel_info['statistics'].get('viewCount', 0),
                    'video_count': len(videos),
                    'collected_date': datetime.now().isoformat(),
                    'day': day_name
                }
                
                self.channels_data.append(channel_data)
                unique_channel_ids.add(channel_id)
                channels_added += 1
                
                print(" ✓")
                
                if channels_added % 10 == 0:
                    self.save_session()
                    time.sleep(1)
            
            time.sleep(1)
        
        print(f"\n{'─'*80}")
        print(f"【{day_name}汇总】")
        print(f"本次采集频道数: {channels_added}")
        print(f"总频道数: {len(self.channels_data)}")
        print(f"配额消耗: {self.quota_used}/10000")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.save_session()
        self.print_statistics()
    
    def print_statistics(self):
        """打印统计信息"""
        print(f"\n{'='*80}")
        print("【当前采集统计】")
        print(f"{'='*80}")
        
        country_stats = {}
        for ch in self.channels_data:
            country = ch['country']
            if country not in country_stats:
                country_stats[country] = 0
            country_stats[country] += 1
        
        for country in ['FR', 'HU', 'LU']:
            count = country_stats.get(country, 0)
            print(f"{country}: {count}/150 频道")
        
        print(f"\n总计: {len(self.channels_data)} 频道")
        print(f"配额使用: {self.quota_used}/10000 单位")
    
    def export_to_collection(self):
        """导出为采集格式"""
        export_data = {
            'total_channels': len(self.channels_data),
            'collection_date': datetime.now().isoformat(),
            'channels': self.channels_data,
            'statistics': {
                'FR': len([ch for ch in self.channels_data if ch['country'] == 'FR']),
                'HU': len([ch for ch in self.channels_data if ch['country'] == 'HU']),
                'LU': len([ch for ch in self.channels_data if ch['country'] == 'LU'])
            }
        }
        
        filename = f"youtube_collection_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ 已导出到: {filename}")
        return filename

def main():
    collector = BatchCollector(YOUTUBE_API_KEY)
    
    print("\n" + "="*80)
    print("YouTube 分批采集工具 v2.0")
    print("="*80)
    print("使用说明:")
    print("  - 根据提示执行对应天数的采集")
    print("  - 每次运行会自动保存进度")
    print("  - 配额用完自动停止，明天继续即可")
    print("="*80 + "\n")
    
    print("选择采集的天数:")
    print("  1 - 第1天 (法国 Part 1)")
    print("  2 - 第2天 (法国 Part 2)")
    print("  3 - 第3天 (匈牙利)")
    print("  4 - 第4天 (卢森堡)")
    print("  1e - 法国扩展 (多领域)")
    print("  3e - 匈牙利扩展 (多领域)")
    print("  4e - 卢森堡扩展 (多领域)")
    print("  5 - 查看统计")
    print("  6 - 导出数据")
    print("  0 - 退出")
    
    while True:
        choice = input("\n请选择 (0-6或1e/3e/4e): ").strip()
        
        if choice == '1':
            collector.collect_batch('Day 1', SEARCH_CONFIG['FR']['day1'], 'FR', 8)
        elif choice == '2':
            collector.collect_batch('Day 2', SEARCH_CONFIG['FR']['day2'], 'FR', 8)
        elif choice == '3':
            collector.collect_batch('Day 3', SEARCH_CONFIG['HU']['day3'], 'HU', 8)
        elif choice == '4':
            collector.collect_batch('Day 4', SEARCH_CONFIG['LU']['day4'], 'LU', 8)
        elif choice == '1e':
            collector.collect_batch('FR Extended', SEARCH_CONFIG['FR']['day1_ext'], 'FR', 8)
        elif choice == '3e':
            collector.collect_batch('HU Extended', SEARCH_CONFIG['HU']['day3_ext'], 'HU', 8)
        elif choice == '4e':
            collector.collect_batch('LU Extended', SEARCH_CONFIG['LU']['day4_ext'], 'LU', 8)
        elif choice == '5':
            collector.print_statistics()
        elif choice == '6':
            collector.export_to_collection()
        elif choice == '0':
            print("退出程序")
            break
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()