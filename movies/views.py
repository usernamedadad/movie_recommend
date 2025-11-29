from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q
from .models import Movie, Rating, Favorite
from .serializers import MovieSerializer, RatingSerializer, FavoriteSerializer

class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))
            
        # Filter by tag
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(alltags__icontains=tag)
            
        # Sort
        sort_by = self.request.query_params.get('sort', None)
        if sort_by == 'hot':
            queryset = queryset.order_by('-view_count')
        elif sort_by == 'rating':
            queryset = queryset.order_by('-star')
        elif sort_by == 'time':
            queryset = queryset.order_by('-years')
            
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        算法推荐接口
        实现：User-Based Collaborative Filtering (基于用户的协同过滤)
        """
        user = request.user
        
        # 1. 冷启动/未登录处理：如果用户未登录或没有评分，返回热门高分电影
        if not user.is_authenticated or not Rating.objects.filter(user=user).exists():
            # 返回 4 部热门电影
            movies = Movie.objects.order_by('-view_count', '-star')[:4]
            serializer = self.get_serializer(movies, many=True)
            return Response(serializer.data)

        # 2. 获取所有评分数据
        ratings = Rating.objects.all().values('user_id', 'movie_id', 'score')
        if not ratings:
            # 没有任何评分数据时，也返回热门电影
            movies = Movie.objects.order_by('-view_count', '-star')[:4]
            serializer = self.get_serializer(movies, many=True)
            return Response(serializer.data)

        # 3. 构建 User-Item 矩阵
        import pandas as pd
        import numpy as np
        
        df = pd.DataFrame(list(ratings))
        user_movie_matrix = df.pivot_table(index='user_id', columns='movie_id', values='score')
        
        # 确保当前用户在矩阵中
        if user.id not in user_movie_matrix.index:
             # 用户不在矩阵中（可能刚注册还没来得及被统计到？虽然前面检查了exists），返回热门
             movies = Movie.objects.order_by('-view_count', '-star')[:4]
             serializer = self.get_serializer(movies, many=True)
             return Response(serializer.data)

        # 4. 计算用户相似度
        # 改用余弦相似度 (Cosine Similarity) 解决评分无方差(如全5分)导致皮尔逊系数无法计算的问题
        user_movie_matrix_filled = user_movie_matrix.fillna(0)
        matrix_values = user_movie_matrix_filled.values
        
        # 计算范数 (L2 Norm)
        norm = np.linalg.norm(matrix_values, axis=1, keepdims=True)
        # 避免除以0
        norm[norm == 0] = 1e-9
        normalized_matrix = matrix_values / norm
        
        # 计算余弦相似度矩阵
        similarity_matrix = np.dot(normalized_matrix, normalized_matrix.T)
        
        # 转为 DataFrame 以便通过 user_id 索引
        user_corr = pd.DataFrame(similarity_matrix, index=user_movie_matrix_filled.index, columns=user_movie_matrix_filled.index)
        
        # 5. 找到相似用户
        if user.id not in user_corr:
             # 无法计算相似度，返回热门
             movies = Movie.objects.exclude(id__in=user_movie_matrix.loc[user.id].dropna().index).order_by('-view_count', '-star')[:4]
             serializer = self.get_serializer(movies, many=True)
             return Response(serializer.data)
             
        similar_users = user_corr[user.id].drop(user.id).sort_values(ascending=False)
        
        # 取前 10 个最相似的用户 (且相关系数 > 0)
        top_similar_users = similar_users[similar_users > 0].head(10)
        
        if top_similar_users.empty:
            # 没有相似用户，返回热门
            movies = Movie.objects.exclude(id__in=user_movie_matrix.loc[user.id].dropna().index).order_by('-view_count', '-star')[:4]
            serializer = self.get_serializer(movies, many=True)
            return Response(serializer.data)

        # 6. 生成推荐列表
        # 逻辑：找到相似用户喜欢(评分>=4)但当前用户没看过的电影
        current_user_watched = user_movie_matrix.loc[user.id].dropna().index
        
        recommend_movie_ids = set()
        for sim_user_id, similarity in top_similar_users.items():
            # 获取该相似用户评分高的电影
            sim_user_ratings = user_movie_matrix.loc[sim_user_id]
            high_rated_movies = sim_user_ratings[sim_user_ratings >= 4.0].index
            
            # 过滤掉当前用户已看过的
            new_movies = [mid for mid in high_rated_movies if mid not in current_user_watched]
            recommend_movie_ids.update(new_movies)
            
            # 限制算法推荐数量为 4 部
            if len(recommend_movie_ids) >= 4:
                break
        
        # 算法推荐结果
        algo_recommend_ids = list(recommend_movie_ids)[:4]
        recommended_movies = list(Movie.objects.filter(id__in=algo_recommend_ids))
        
        # 7. 固定补充热门电影 (Fixed Popular Movies)
        # 无论算法是否有结果，都额外获取 4 部热门电影（排除已看过的和已经在算法推荐里的）
        popular_movies = Movie.objects.exclude(id__in=current_user_watched)\
                                      .exclude(id__in=algo_recommend_ids)\
                                      .order_by('-view_count', '-star')[:4]
        
        # 将热门电影添加到推荐列表中
        recommended_movies.extend(popular_movies)

        serializer = self.get_serializer(recommended_movies, many=True)
        return Response(serializer.data)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure one rating per movie per user? Or allow updates?
        # For now, simple create.
        serializer.save(user=self.request.user)

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
