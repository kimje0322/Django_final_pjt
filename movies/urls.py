from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.index, name='index'),
    path('movie/', views.movie_list, name='movie_list'),
    path('movie/<int:movie_pk>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_pk>/create/', views.review_create, name='review_create'),
    path('movie/<int:movie_pk>/<int:review_pk>/', views.review_detail, name='review_detail'),
    path('movie/<int:movie_pk>/update/<int:review_pk>', views.review_update, name='review_update'),
    path('movie/<int:movie_pk>/delete/<int:review_pk>', views.review_delete, name='review_delete'),
    path('movie/<int:movie_pk>/<int:review_pk>/create', views.comment_create, name='comment_create'),
    path('movie/<int:movie_pk>/<int:review_pk>/<int:comment_pk>/update', views.comment_update, name='comment_update'),
    path('movie/<int:movie_pk>/<int:review_pk>/<int:comment_pk>/delete', views.comment_delete, name='comment_delete'),
    path('movie/<int:movie_pk>/like/', views.like_movie, name='like_movie'),
    path('movie/<int:movie_pk>/<int:review_pk>/like', views.like_review, name='like_review'),
    path('movie/<int:movie_pk>/scrap/', views.scrap_movie, name='scrap_movie'),
    path('recommend/', views.recommend, name="recommend"),
    path('recommend/<int:recommend_pk>/', views.recommend_list, name="recommend_list"),
    path('movie/search/', views.movie_search, name="movie_search"),
]