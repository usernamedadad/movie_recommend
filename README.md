# 电影推荐系统

简要说明  
一个基于 TMDB 数据的电影展示与推荐系统。后端 Django + DRF，前端 Bootstrap3 + jQuery，支持用户注册/登录、评分、收藏、个人中心与基于用户协同过滤的“猜你喜欢”。

核心功能
- 影片展示：海报、标题、评分、详情弹窗
- 分类/排序/搜索：按热门、评分、时间等排序与关键字搜索
- 用户交互：注册、登录、评分、收藏、取消收藏、删除评分
- 个人中心：查看我的收藏与我的评分
- 推荐系统：“猜你喜欢”基于用户协同过滤输出个性化推荐（算法推荐 + 热门补充）

技术栈
- 后端：Python 3.12.7、Django 5.2.8、Django REST Framework
- 前端：Bootstrap 3、jQuery
- 数据处理/算法：pandas、numpy
- 数据库：SQLite

算法原理
- 策略：User-Based 协同过滤（User-CF）
- 相似度：默认使用余弦相似度（Cosine）以避免评分方差为 0 导致 Pearson 失效的问题
- 推荐流程：
  1. 汇总用户-电影评分矩阵
  2. 计算当前用户与其他用户相似度（余弦）
  3. 从相似用户的高评分电影中挑选候选（排除已评分电影）
  4. 返回最多 3–4 条算法推荐；若不足则追加 3–4 条热门电影（按浏览量/评分）作为补充
- 注意：Pearson 可替代余弦，但要求用户评分具有非零方差；在稀疏或常量评分场景下会失效

激活与运行（Windows PowerShell）
```powershell
cd 项目根目录

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 安装依赖
pip install django djangorestframework pandas numpy requests

# 数据库迁移与导入
python  makemigrations
python  migrate

# 启动开发服务器
python  runserver

# 访问
# 主站/登录: http://127.0.0.1:8000/
# 管理后台: http://127.0.0.1:8000/admin/  (需 createsuperuser)
