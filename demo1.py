import requests
import pandas as pd
import time
import os

# ================= 配置区域 =================
API_KEY = '4615d1c8c5f6c47476f1914297a71704' 
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500' # 图片前缀
LANGUAGE = 'zh-CN'
TARGET_COUNT = 2000  # 目标数量

# 【新增】代理设置
# TMDB 在国内无法直接访问，必须配置代理。
# 请查看你的 VPN/代理软件的“本地端口”设置。
# 常见端口：Clash (7890), v2rayN (10809), SSR (1080)
# 如果你的端口不是 7890，请手动修改下面的数字
PROXIES = {
    'http': 'http://127.0.0.1:10809',
    'https': 'http://127.0.0.1:10809'
}
# ===========================================

def get_movie_details(movie_id):
    """获取单部电影的详细信息（包含导演、演员、国家等）"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        'api_key': API_KEY,
        'language': LANGUAGE,
        'append_to_response': 'credits' # 额外请求演职员表
    }
    
    try:
        # 加上 proxies 参数
        response = requests.get(url, params=params, timeout=10, proxies=PROXIES)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # 1. 提取基础信息
        title = data.get('title', '')
        image_link = IMAGE_BASE_URL + data.get('poster_path', '') if data.get('poster_path') else ""
        years = data.get('release_date', '')[:4] if data.get('release_date') else ""
        description = data.get('overview', '').replace('\n', ' ')
        star = data.get('vote_average', 0)
        time_length = f"{data.get('runtime', 0)}分钟"
        imdb_id = data.get('imdb_id', '')
        
        # 2. 提取国家和语言
        countries = [c['name'] for c in data.get('production_countries', [])]
        country = "/".join(countries) if countries else "未知"
        
        original_lang = data.get('original_language', '')
        
        # 3. 提取标签 (Genres)
        genres = [g['name'] for g in data.get('genres', [])]
        alltags = "/".join(genres)
        
        # 4. 提取导演和主演 (从 credits 中)
        credits = data.get('credits', {})
        
        # 导演
        directors = [crew['name'] for crew in credits.get('crew', []) if crew['job'] == 'Director']
        director_description = "/".join(directors[:3]) # 取前3个导演
        
        # 主演 (Leader)
        cast = [actor['name'] for actor in credits.get('cast', [])]
        leader = "/".join(cast[:5]) # 取前5个主演
        
        return {
            'id': movie_id, 
            'title': title,
            'image_link': image_link,
            'country': country,
            'years': years,
            'director_description': director_description,
            'leader': leader,
            'star': star,
            'description': description,
            'alltags': alltags,
            'imdb': imdb_id,
            'language': original_lang,
            'time_length': time_length
        }
        
    except Exception as e:
        print(f"Error fetching details for {movie_id}: {e}")
        return None

def fetch_movies():
    movies_data = []
    page = 1
    
    print(f"开始从 TMDB 获取数据，目标: {TARGET_COUNT} 条...")
    
    while len(movies_data) < TARGET_COUNT:
        # 使用 'discover' 接口按热度排序获取电影列表
        discover_url = f"{BASE_URL}/discover/movie"
        params = {
            'api_key': API_KEY,
            'language': LANGUAGE,
            'sort_by': 'popularity.desc', # 按热度降序
            'page': page
        }
        
        try:
            # 加上 proxies 参数
            res = requests.get(discover_url, params=params, timeout=10, proxies=PROXIES)
            if res.status_code != 200:
                print(f"Page {page} request failed.")
                break
                
            results = res.json().get('results', [])
            if not results:
                break
                
            print(f"正在处理第 {page} 页，本页 {len(results)} 条数据...")
            
            for item in results:
                if len(movies_data) >= TARGET_COUNT:
                    break
                
                # 获取详情 (列表页信息不全，需要再次请求详情页)
                detail = get_movie_details(item['id'])
                if detail:
                    movies_data.append(detail)
                    # 打印进度
                    if len(movies_data) % 50 == 0:
                        print(f"已收集 {len(movies_data)} 条...")
                
            page += 1
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            time.sleep(2) # 出错稍微停一下
            
    # 保存
    if movies_data:
        df = pd.DataFrame(movies_data)
        # 保存到当前脚本所在目录
        output_path = os.path.join(os.path.dirname(__file__), 'tmdb_movies_2000.csv')
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n成功!数据已保存至 {output_path}")
        print(f"共获取 {len(df)} 条电影数据。")
        print(df[['title', 'years', 'country']].head())
    else:
        print("未获取到数据。")

if __name__ == "__main__":
    fetch_movies()