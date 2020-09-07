from django import forms
from .models import Review, Comment, Recommend

class ReviewForm(forms.ModelForm):
    REVIEW_RANK_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    )
    rank = forms.ChoiceField(choices = REVIEW_RANK_CHOICES)
    class Meta:
        model = Review
        fields = ['title', 'content', 'rank']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class RecommendForm(forms.ModelForm):
    GENRE_CHOICES = (
    ('0', '선택안함'),
	('12', 'Adventure'),
    ('14', 'Fantasy'),
    ('16', 'Animation'),
    ('18', 'Drama'),
    ('27', 'Horror'),
    ('28', 'Action'),
    ('35', 'Comedy'),
    ('36', 'History'),
    ('37', 'Western'),
    ('53', 'Thriller'),
    ('80', 'Crime'),
    ('99', 'Documentary'),
    ('878', 'Science Fiction'),
    ('9648', 'Mystery'),
    ('10402', 'Music'),
    ('10749', 'Romance'),
    ('10751', 'Family'),
    ('10752', 'War'),
    ('10770', 'TV Movie'),
    )
    RANK_CHOICES = (
    (0, '선택안함'),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (10, 10),
    )
    RELEASE_YEAR_CHOICES = (
    (0, '선택안함'),
    (2020, '2015 ~ 2020'),
    (2015, '2010 ~ 2015'),
    (2010, '2005 ~ 2010'),
    (2005, '2000 ~ 2005'),
    (2000, '1995 ~ 2000'),
    (1995, '1990 ~ 1995'),
    (1990, '1985 ~ 1990'),
    (1985, '1980 ~ 1985'),
    (1980, '1975 ~ 1980'),
    (1975, '1970 ~ 1975'),
    )
    genre = forms.ChoiceField(choices = GENRE_CHOICES)
    rank = forms.ChoiceField(choices = RANK_CHOICES)
    date = forms.ChoiceField(choices = RELEASE_YEAR_CHOICES)
    class Meta():
        model = Recommend
        fields = ['genre', 'rank', 'release_date']