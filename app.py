from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

def fetch_poster(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key=1cf50e6248dc270629e802686245c2c8&language=en-US"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching movie data: {response.status_code}")
        return ""
    
    data = response.json()
    poster_path = data.get('poster_path')  # Safely get poster_path
    if not poster_path:
        print("Poster path not found for movie ID:", id)
        return ""
    
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"  # Construct full poster URL
    return full_path

# https://api.themoviedb.org/3/discover/movie?sort_by=popularity.desc&/api_key=1cf50e6248dc270629e802686245c2c8

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(id))  # Fetch poster URL

    return recommended_movies, recommended_posters


# Load data
movies_dict = pickle.load(open('model/movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html', movie_list=movies['title'].values)

@app.route('/recommend', methods=['POST'])
def recommend_movies():
    movie_name = request.form['movie']
    recommended_movies, recommended_posters = recommend(movie_name)
    # Zip the movie names and posters together
    movies_and_posters = zip(recommended_movies, recommended_posters)
    return render_template('recommend.html', 
                           movie_name=movie_name, 
                           movies_and_posters=movies_and_posters)

if __name__ == '__main__':
    app.run(debug=True)
