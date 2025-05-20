import streamlit as st
import pickle
import requests
import streamlit.components.v1 as components

# --- Fetch poster with error handling ---
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    except requests.exceptions.Timeout:
        st.warning(f"⚠️ Timeout for movie ID: {movie_id}")
    except requests.exceptions.RequestException as e:
        st.warning(f"⚠️ Network error for movie ID: {movie_id} - {e}")
    except Exception as e:
        st.warning(f"⚠️ Error for movie ID: {movie_id} - {e}")
    return None

# --- Load Data ---
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))

# Clean and get unique movie titles
movies['title_clean'] = movies['title'].str.strip().str.lower()
unique_titles = sorted(set(movies['title'].str.strip()))
st.header("🎬 Movie Recommender System")

# --- Image Carousel Component ---
imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")

# --- Static Posters for Carousel ---
static_movie_ids = [1632, 299536, 17455, 2830, 429422, 9722, 13972, 240, 155, 598, 914, 255709, 572154]
imageUrls = [fetch_poster(mid) for mid in static_movie_ids]
imageUrls = [url for url in imageUrls if url]  # filter out None
imageCarouselComponent(imageUrls=imageUrls, height=200)

# --- Movie Selector ---
selectvalue = st.selectbox("🎞️ Select a movie", unique_titles)

# --- Recommendation Function ---
def recommend(movie_title_input):
    # Normalize selected title
    movie_title_clean = movie_title_input.strip().lower()
    
    # Find matching movie row
    match = movies[movies['title_clean'] == movie_title_clean]
    if match.empty:
        st.error("❌ Selected movie not found in dataset.")
        return [], []

    index = match.index[0]
    distances = list(enumerate(similarity[index]))
    sorted_distances = sorted(distances, reverse=True, key=lambda x: x[1])

    recommend_movie = []
    recommend_poster = []

    for i in sorted_distances[1:11]:  # Check more in case some posters fail
        movie_id = movies.iloc[i[0]].id
        poster_url = fetch_poster(movie_id)
        if poster_url:
            recommend_movie.append(movies.iloc[i[0]].title)
            recommend_poster.append(poster_url)
        if len(recommend_movie) == 5:
            break

    st.write(f"✅ Found {len(recommend_movie)} recommendations for '{movie_title_input}'.")
    return recommend_movie, recommend_poster

# --- Show Recommendations Safely ---
if st.button("Show Recommend"):
    movie_name, movie_poster = recommend(selectvalue)

    if len(movie_name) == 0:
        st.warning("No valid recommendations found. Try a different movie.")
    else:
        cols = st.columns(len(movie_name))
        for i in range(len(movie_name)):
            with cols[i]:
                st.text(movie_name[i])
                st.image(movie_poster[i])
