from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    """
    电影模型
    对应爬取的 tmdb_movies_2000.csv 中的字段
    """
    # 使用 TMDB 的 ID 作为主键，方便后续更新和索引
    id = models.IntegerField(primary_key=True, verbose_name="TMDB ID")
    
    title = models.CharField(max_length=255, verbose_name="电影名称")
    image_link = models.URLField(max_length=500, verbose_name="封面图片链接")
    country = models.CharField(max_length=100, verbose_name="制片国家/地区")
    years = models.CharField(max_length=10, verbose_name="年代")
    
    # 导演和主演可能较长，给够空间
    director_description = models.CharField(max_length=500, verbose_name="导演", blank=True)
    leader = models.CharField(max_length=1000, verbose_name="主演", blank=True)
    
    # TMDB 的平均评分 (0-10分)
    star = models.FloatField(default=0.0, verbose_name="TMDB评分")
    
    description = models.TextField(verbose_name="简介", blank=True)
    
    # 标签/类型，如 "剧情/爱情"
    alltags = models.CharField(max_length=255, verbose_name="类型标签", blank=True)
    
    imdb = models.CharField(max_length=50, verbose_name="IMDb ID", blank=True)
    language = models.CharField(max_length=50, verbose_name="语言", blank=True)
    time_length = models.CharField(max_length=50, verbose_name="时长", blank=True)

    # 新增字段：浏览量，用于热门排序
    view_count = models.IntegerField(default=0, verbose_name="浏览量")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "电影"
        verbose_name_plural = "电影列表"


class Rating(models.Model):
    """
    评分模型
    用于协同过滤算法 (User-Item-Rating)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="电影")
    score = models.FloatField(verbose_name="评分") # 1.0 - 5.0
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="评分时间")

    class Meta:
        verbose_name = "用户评分"
        verbose_name_plural = "用户评分列表"

class Favorite(models.Model):
    """
    收藏模型
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="电影")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name = "收藏"
        verbose_name_plural = "收藏列表"
