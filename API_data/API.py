import json
import requests

# 영화 JSON 파일 받아오기 (original)
data = {"results": []}
for i in range(1, 6):
    API_URL = f'https://api.themoviedb.org/3/movie/popular?api_key=ed87f11a9d1a8ca94369a8acb370c42a&language=ko-KR&page={i}'
    response = requests.get(API_URL).json()
    for value in response["results"]:
        data["results"].append(value)
movie_data_original = data

with open('moviedata_init.json', 'w') as f:
    json.dump(movie_data_original, f, indent=4)

final_data = list()

# 영화 장르 데이터 Django json형식으로 변환
with open('moviegenre.json', 'r', encoding='UTF8') as f:
    genre_json_data = json.load(f)

genre_datas = genre_json_data["genres"]
for genre_data in genre_datas:
    genre_data["model"] = "movies.genre"
    genre_data["pk"] = genre_data.pop("id")
    genre_data["fields"] = {"name": genre_data.pop("name")}
    final_data.append(genre_data)

# 영화 데이터 Django json 데이터 형식으로 변환
with open('moviedata_add.json', 'r', encoding='UTF8') as f:
    movie_json_data = json.load(f)

movie_datas = movie_json_data["results"]
key_name = set()
for movie_data in movie_datas:
    movie_data["model"] = "movies.movie"
    movie_data["pk"] = movie_data.pop("id")
    movie_data["fields"] = {}
    for key, value in movie_data.items():
        if key != "model" and key != "pk" and key != "fields":
            movie_fields = movie_data["fields"]
            movie_fields[key] = value
            key_name.add(key)

for movie_data in movie_datas:
    for key in key_name:
        del(movie_data[key])

for movie_data in movie_datas:
    if movie_data["fields"]["adult"] == False:
        final_data.append(movie_data)

with open('moviedata.json', 'w') as f:
    json.dump(final_data, f, indent=4)