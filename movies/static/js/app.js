$(document).ready(function() {
    var currentPage = 1;
    var currentSort = 'default';
    var currentSearch = '';

    loadMovies(currentPage, currentSort, currentSearch);

    // Filter buttons
    $('.filter-btn').click(function() {
        $('.filter-btn').removeClass('active');
        $(this).addClass('active');
        currentSort = $(this).data('sort');
        currentPage = 1;
        loadMovies(currentPage, currentSort, currentSearch);
    });

    // Search
    $('#search-btn').click(function() {
        currentSearch = $('#search-input').val();
        currentPage = 1;
        loadMovies(currentPage, currentSort, currentSearch);
    });

    // Navigation
    $('#nav-hot').click(function() {
        $('.filter-btn[data-sort="hot"]').click();
    });
    $('#nav-top').click(function() {
        $('.filter-btn[data-sort="rating"]').click();
    });
    $('#nav-recommend').click(function() {
        // Reset filters
        $('.filter-btn').removeClass('active');
        $('#search-input').val('');
        
        loadRecommendations();
    });

    function loadRecommendations() {
        $.ajax({
            url: '/api/movies/recommendations/',
            type: 'GET',
            success: function(data) {
                // Recommendations endpoint returns a list, not a paginated object
                $('#pagination').html(''); // Clear pagination
                $('#filter-bar').hide(); // Hide filters for recommendation view

                if (!data || data.length === 0) {
                    $('#movie-list').html('<div class="col-md-12 text-center">暂无推荐。请先为几部电影评分以获得个性化推荐。</div>');
                } else {
                    renderMovies(data);
                }
            },
            error: function(err) {
                console.error('Error loading recommendations:', err);
                $('#movie-list').html('<div class="col-md-12 text-center text-danger">加载推荐失败，请稍后再试。</div>');
            }
        });
    }

    function loadMovies(page, sort, search) {
        $('#filter-bar').show(); // Ensure filters are visible
        var url = '/api/movies/?page=' + page;
        if (sort && sort !== 'default') {
            url += '&sort=' + sort;
        }
        if (search) {
            url += '&search=' + search;
        }

        $.ajax({
            url: url,
            type: 'GET',
            success: function(data) {
                renderMovies(data.results);
                renderPagination(data.count, page);
            },
            error: function(err) {
                console.error('Error loading movies:', err);
                $('#movie-list').html('<div class="col-md-12 text-center text-danger">加载失败，请检查后端服务。</div>');
            }
        });
    }

    function renderMovies(movies) {
        var html = '';
        if (movies.length === 0) {
            html = '<div class="col-md-12 text-center">没有找到相关电影。</div>';
        } else {
            $.each(movies, function(index, movie) {
                var imgUrl = movie.image_link;
                if (!imgUrl) imgUrl = 'https://via.placeholder.com/300x450?text=No+Image';
                
                html += '<div class="col-md-3 col-sm-6">';
                html += '  <div class="thumbnail movie-card">';
                html += '    <img src="' + imgUrl + '" alt="' + movie.title + '" class="movie-img" onerror="this.src=\'https://via.placeholder.com/300x450?text=Error\'">';
                html += '    <div class="caption">';
                html += '      <h4 title="' + movie.title + '">' + movie.title + '</h4>';
                html += '      <p>评分: <span class="text-warning">' + movie.star + '</span></p>';
                html += '      <p><a href="#" class="btn btn-primary btn-sm view-details" data-id="' + movie.id + '" role="button">详情</a></p>';
                html += '    </div>';
                html += '  </div>';
                html += '</div>';
                
                // Add clearfix for Bootstrap 3 grid system to prevent misalignment
                if ((index + 1) % 4 === 0) {
                    html += '<div class="clearfix visible-md-block visible-lg-block"></div>';
                }
                if ((index + 1) % 2 === 0) {
                    html += '<div class="clearfix visible-sm-block"></div>';
                }
            });
        }
        $('#movie-list').html(html);

        // Bind click event for details
        $('.view-details').click(function(e) {
            e.preventDefault();
            var movieId = $(this).data('id');
            loadMovieDetail(movieId);
        });
    }

    // CSRF Token setup for AJAX
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    var currentMovieId = null;

    function loadMovieDetail(id) {
        currentMovieId = id;
        // Reset UI
        $('#rating-msg').hide();
        $('#rating-group label').removeClass('active');
        
        $.ajax({
            url: '/api/movies/' + id + '/',
            type: 'GET',
            success: function(movie) {
                $('#modal-title').text(movie.title);
                $('#modal-img').attr('src', movie.image_link);
                $('#modal-year').text(movie.years);
                $('#modal-country').text(movie.country);
                $('#modal-star').text(movie.star);
                $('#modal-director').text(movie.director_description);
                $('#modal-cast').text(movie.leader);
                $('#modal-tags').text(movie.alltags);
                $('#modal-desc').text(movie.description);
                $('#movieModal').modal('show');
            }
        });
    }

    // Submit Rating
    $('#submit-rating').click(function() {
        var score = $('input[name="rating"]:checked').val();
        if (!score) {
            alert('请选择评分');
            return;
        }
        if (!currentMovieId) return;

        $.ajax({
            url: '/api/ratings/',
            type: 'POST',
            data: {
                movie: currentMovieId,
                score: score
            },
            success: function() {
                $('#rating-msg').text('评分成功').show().fadeOut(2000);
            },
            error: function(xhr) {
                if (xhr.status === 403) {
                    alert('请先登录');
                } else {
                    alert('评分失败');
                }
            }
        });
    });

    // Add to Favorites
    $('#btn-favorite').click(function() {
        if (!currentMovieId) return;
        $.ajax({
            url: '/api/favorites/',
            type: 'POST',
            data: {
                movie: currentMovieId
            },
            success: function() {
                alert('收藏成功');
            },
            error: function(xhr) {
                if (xhr.status === 400) {
                    // Likely already favorited (unique constraint)
                    alert('您已收藏过该电影');
                } else if (xhr.status === 403) {
                    alert('请先登录');
                } else {
                    alert('收藏失败');
                }
            }
        });
    });

    function renderPagination(totalCount, currentPage) {
        // Simple pagination logic
        var pageSize = 10; // Matches DRF setting
        var totalPages = Math.ceil(totalCount / pageSize);
        var html = '';
        
        if (totalPages > 1) {
            var startPage = Math.max(1, currentPage - 2);
            var endPage = Math.min(totalPages, currentPage + 2);

            if (currentPage > 1) {
                html += '<li><a href="#" onclick="return false;" class="page-link" data-page="' + (currentPage - 1) + '">&laquo;</a></li>';
            }

            for (var i = startPage; i <= endPage; i++) {
                var activeClass = (i === currentPage) ? 'active' : '';
                html += '<li class="' + activeClass + '"><a href="#" onclick="return false;" class="page-link" data-page="' + i + '">' + i + '</a></li>';
            }

            if (currentPage < totalPages) {
                html += '<li><a href="#" onclick="return false;" class="page-link" data-page="' + (currentPage + 1) + '">&raquo;</a></li>';
            }
        }
        
        $('#pagination').html(html);

        $('.page-link').click(function() {
            var page = $(this).data('page');
            currentPage = page;
            loadMovies(currentPage, currentSort, currentSearch);
            $('html, body').animate({ scrollTop: 0 }, 'fast');
        });
    }
});
