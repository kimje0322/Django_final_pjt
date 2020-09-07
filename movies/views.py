from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum
from .models import Movie, Genre, Review, Comment, Recommend
from .forms import ReviewForm, CommentForm, RecommendForm
import requests, os


def index(request):
    movies = Movie.objects.order_by('-vote_average')[:10]
    # 추천 알고리즘
    recommend_movies = []
    sort_recommend = []
    total = 0
    num = list()
    if request.user.is_authenticated:
        if request.user.like_movies.all():
            recommend_genre = {}
            for like_movie in request.user.like_movies.all():
                for genre_id in like_movie.genre_ids.all():
                    if genre_id in recommend_genre.keys():
                        recommend_genre[genre_id] += 1
                    else:
                        recommend_genre[genre_id] = 1
            sort_recommend = sorted(recommend_genre.items(), key=(lambda x:x[1]), reverse=True)
            if len(sort_recommend) >= 3:
                sort_recommend = sort_recommend[:3]

            for key, value in sort_recommend:
                total += value
            count = 10
            for idx in range(len(sort_recommend)):
                if idx == len(sort_recommend) - 1:
                    num.append(int(count))
                else:
                    number = round(sort_recommend[idx][1] / total, 1) * 10   # 5, 3, 2
                    count -= number
                    num.append(int(number))
            for idx in range(len(num)-1, -1, -1):
                items = Movie.objects.filter(genre_ids=sort_recommend[idx][0].id).order_by('-popularity')[:num[idx]]
                for item in items:
                    cnt = 0
                    while item in recommend_movies:
                        cnt += 1
                        items = Movie.objects.filter(genre_ids=sort_recommend[idx][0].id).order_by('-popularity')
                        if cnt >= len(items):
                            item = Movie.objects.order_by('?')[1]
                            break
                        else:
                            item = items[cnt]
                    recommend_movies.append(item)
        # 좋아요한 영화가 없는 경우
        else:
            items = Movie.objects.all().order_by('?')[:10]
            recommend_movies = items
    else:
        items = Movie.objects.all().order_by('?')[:10]
        recommend_movies = items

    # 최신 영화
    latest_movies = Movie.objects.order_by('-release_date')[:10]
    # 최신 영화(예고편)
    latest_movie = Movie.objects.order_by('-release_date')[:3]
    YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3/search'
    MOVIE_URL = []
    for movie in latest_movie:
        back_img = f'https://image.tmdb.org/t/p/original{movie.backdrop_path}'
        params = {
            # 'key': os.environ.get("YOUTUBE_API_KEY"),
            'key': 'AIzaSyDE-_9YKasVUcXLg830rVZ32EL8JYjl_2w',
                # 'AIzaSyCSlvLPNLSZ9Jw7j_MlJhIkDne8LwwlV3k',
            'part': 'snippet',
            'type': 'video',
            'maxResult': '1',
            'q': f'{movie.original_title} trailer',
        }
        response = requests.get(YOUTUBE_URL, params)
        response_dict = response.json()
        VIDEO_URL = f'https://www.youtube.com/embed/{response_dict["items"][0]["id"]["videoId"]}'
        MOVIE_URL.append((movie, VIDEO_URL))
    # 최근 리뷰
    latest_review = Review.objects.order_by('-created_at')[0]
    reviews = Review.objects.order_by('-created_at')[1:5]
    context = {
        'movies': movies,
        'recommend_movies': recommend_movies,
        'latest_movies': latest_movies,
        'MOVIE_URL': MOVIE_URL,
        'latest_review': latest_review,
        'reviews': reviews,
    }
    return render(request, 'movies/index.html', context)

def movie_list(request):
    movies = Movie.objects.order_by('-vote_average')
    paginator = Paginator(movies, 15)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)
    context = {
        'movies': movies,
        'page_num': page_num,
        'page_obj': page_obj,
    }
    return render(request, 'movies/movie_list.html', context)

def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    back_img = f'https://image.tmdb.org/t/p/original{movie.backdrop_path}'
    YOUTUBE_URL = 'https://www.googleapis.com/youtube/v3/search'
    MOVIE_URL = []
    for word in ['예고편', '시사회']:
        params = {
            # 'key': os.environ.get("YOUTUBE_API_KEY"),
            'key':'AIzaSyDE-_9YKasVUcXLg830rVZ32EL8JYjl_2w',
                # 'AIzaSyCSlvLPNLSZ9Jw7j_MlJhIkDne8LwwlV3k',
            'part': 'snippet',
            'type': 'video',
            'maxResult': '1',
            'q': f'{movie.original_title} + {word}',
        }
        response = requests.get(YOUTUBE_URL, params)
        response_dict = response.json()
        VIDEO_URL = f'https://www.youtube.com/embed/{response_dict["items"][0]["id"]["videoId"]}'
        MOVIE_URL.append((word, VIDEO_URL))
    context = {
        'movie': movie,
        'back_img': back_img,
        'MOVIE_URL': MOVIE_URL,
        'response_dict': response_dict,
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review_num = Review.objects.filter(movie=movie_pk).count()
    rank_sum = Review.objects.filter(movie=movie_pk).aggregate(Sum('rank'))["rank__sum"]
    if not rank_sum:
        rank_sum = 0
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.movie_id = movie_pk
            movie.vote_average = round((movie.vote_average + rank_sum) / (review_num + 1), 1)
            movie.save()
            review.save()
            return redirect('movies:movie_detail', movie_pk)
    else:
        form = ReviewForm()
    context = {
        'form': form,
        'rank_sum': rank_sum,
        'review_num': review_num,
    }
    return render(request, 'movies/review_form.html', context)


def review_detail(request, movie_pk, review_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    review = get_object_or_404(Review, pk=review_pk)
    back_img = f'https://image.tmdb.org/t/p/original{movie.backdrop_path}'
    context = {
        'movie': movie,
        'review': review,
        'back_img': back_img,
    }
    return render(request, 'movies/review_detail.html', context)

@login_required
def review_update(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie_id = movie_pk
                review.save()
                return redirect('movies:review_detail', movie_pk, review_pk)
        else:
            form = ReviewForm(instance=review)
        context = {
            'form': form
        }
        return render(request, 'movies/review_form.html', context)
    else:
        message.warning(request, '본인 글만 수정 가능합니다.')
        return redirect('movies:movie_detail', movie_pk)

@require_POST
@login_required
def review_delete(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.user == review.user:
        review.delete()
    return redirect('movies:movie_detail', movie_pk)

@login_required
def comment_create(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.review = review
            comment.save()
            return redirect('movies:review_detail', movie_pk, review_pk)
    else:
        form = CommentForm()
    context = {
        'form': form,
    }
    return render(request, 'movies/comment_form.html', context)

@login_required
def comment_update(request, movie_pk, review_pk, comment_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        if request.method == 'POST':
            form = CommentForm(request.POST, instance=comment)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = request.user
                comment.review = review
                comment.save()
                return redirect('movies:review_detail', movie_pk, review_pk)
        else:
            form = CommentForm(instance=comment)
        context = {
            'form': form
        }
        return render(request, 'movies/comment_form.html', context)
    else:
        message.warning(request, '본인 댓글만 수정 가능합니다.')
        return redirect('movies:review_detail', movie_pk, review_pk)

@require_POST
@login_required
def comment_delete(request, movie_pk, review_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    if request.user == comment.user:
        comment.delete()
    return redirect('movies:review_detail', movie_pk, review_pk)

@login_required
def like_movie(request, movie_pk):
    user = request.user
    movie = get_object_or_404(Movie, pk=movie_pk)

    if movie.like_users.filter(pk=user.pk).exists():
        movie.like_users.remove(user)
        liked = False
    else:
        movie.like_users.add(user)
        liked = True

    context = {
        'liked': liked,
        'like_count': movie.like_users.count(),
    }
    return JsonResponse(context)

@login_required
def like_review(request, movie_pk, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    if review.like_users.filter(id=request.user.pk).exists():
        review.like_users.remove(request.user)
    else:
        review.like_users.add(request.user)
    return redirect('movies:review_detail', movie_pk, review_pk)

@login_required
def scrap_movie(request, movie_pk):
    user = request.user
    movie = get_object_or_404(Movie, pk=movie_pk)
    if movie.scrap_users.filter(id=request.user.pk).exists():
        movie.scrap_users.remove(request.user)
        scrapped = False
    else:
        movie.scrap_users.add(request.user)
        scrapped = True

    context = {
        'scrapped': scrapped,
        'scrap_count': movie.scrap_users.count(),
    }
    print(context)
    return JsonResponse(context)

@login_required
def recommend(request):
    if request.method == 'POST':
        form = RecommendForm(request.POST)
        if form.is_valid():
            recommend = form.save()
            # if not recommend.release_date:
            #     recommend.release_date = '1000-01-01'
            # recommend.save()
            return redirect('movies:recommend_list', recommend.pk)
    else:
        form = RecommendForm()
    context = {
        'form': form,
    }
    return render(request, 'movies/movie_recommend.html', context)

def recommend_list(request, recommend_pk):
    recommend = get_object_or_404(Recommend, pk=recommend_pk)

    # 장르를 선택안함
    if recommend.genre == '0':
        # 평점 선택안함
        if not recommend.vote_average:
            if recommend.release_date.year == 1000:
                movies = Movie.objects.order_by('-vote_average')
            else:
                movies = Movie.objects.filter(release_date__year__gte=int(recommend.release_date.year)-5, release_date__year__lte=recommend.release_date.year)
        # 평점 선택
        else:
            # 개봉일 선택안함
            if recommend.release_date.year == 1000:
                movies = Movie.objects.filter(vote_average__gte=recommend.vote_average)
            # 개봉일 선택
            else:
                movies = Movie.objects.filter(vote_average__gte=recommend.vote_average).filter(release_date__year__gte=int(recommend.release_date.year)-5, release_date__year__lte=recommend.release_date.year)
    else:
        if not recommend.vote_average:
            if recommend.release_date.year == 1000:
                movies = Movie.objects.filter(genre_ids=recommend.genre)
            else:
                movies = Movie.objects.filter(genre_ids=recommend.genre).filter(release_date__year__gte=int(recommend.release_date.year)-5, release_date__year__lte=recommend.release_date.year)
        else:
            if recommend.release_date.year == 1000:
                movies = Movie.objects.filter(genre_ids=recommend.genre).filter(vote_average__gte=recommend.vote_average)
            else:
                movies = Movie.objects.filter(genre_ids=recommend.genre).filter(vote_average__gte=recommend.vote_average).filter(release_date__year__gte=int(recommend.release_date.year)-5, release_date__year__lte=recommend.release_date.year)

    paginator = Paginator(movies, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'movies': movies,
        'page_number':page_number,
        'page_obj': page_obj,
        'recommend': recommend,
    }
    return render(request, 'movies/recommend_list.html', context)


def movie_search(request):
    keyword = request.GET.get('message')
    if keyword == '':
        movies = []
    else:
        movies = Movie.objects.filter(Q(title__contains=keyword)|Q(original_title__contains=keyword))

    paginator = Paginator(movies, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'keyword': keyword,
        'movies': movies,
        'page_number':page_number,
        'page_obj': page_obj,

    }
    return render(request, 'movies/movie_search.html', context)
