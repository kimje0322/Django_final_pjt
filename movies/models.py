from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=20)

class Movie(models.Model):
    popularity = models.FloatField()
    vote_count = models.IntegerField()
    video = models.BooleanField()
    poster_path = models.CharField(max_length=500)
    adult = models.BooleanField()
    backdrop_path = models.CharField(max_length=500, null=True)
    original_language = models.CharField(max_length=20)
    original_title = models.CharField(max_length=100)
    genre_ids = models.ManyToManyField(Genre, related_name='movie')
    title = models.CharField(max_length=100)
    vote_average = models.FloatField()
    overview = models.TextField()
    release_date = models.DateField()
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_movies')
    scrap_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scrap_movies')

class Review(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rank = models.IntegerField()
    spo = models.BooleanField()
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_reviews')

class Comment(models.Model):
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

class Recommend(models.Model):
    genre = models.CharField(max_length=100)
    vote_average = models.IntegerField(null=True)
    release_date = models.DateField(null=True)

