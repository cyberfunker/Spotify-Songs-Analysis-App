import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
import pandas as pd
import streamlit as st

client_credentials_manager = SpotifyClientCredentials(client_id=st.secrets["SPOTIFY_ID"], client_secret=st.secrets["SPOTIFY_SECRET"])
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)  # ACCESS THE API


@st.cache(suppress_st_warning=True, show_spinner=False)
def busca_artista(busca):
    begin_time = time.time()  # to calculate the time it takes to process everything

    # Search for artist
    result = sp.search(busca, type="artist")

    artist_uri = result["artists"]["items"][0]["uri"]
    artist = result["artists"]["items"][0]["name"]

    # Pull all of the artist's albums
    sp_albums = sp.artist_albums(artist_uri)

    # Store artist's albums' names' and uris in separate lists
    album_names = []
    album_uris = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])

    # Keep names and uris in same order to keep track of duplicate albums

    def albumSongs(album_uri):
        spotify_albums[album_uri] = {}  # Creates dictionary for that specific album
        # Create keys-values of empty lists inside nested dictionary for album
        spotify_albums[album_uri]['album'] = []  # create empty list
        spotify_albums[album_uri]['track_number'] = []
        spotify_albums[album_uri]['id'] = []
        spotify_albums[album_uri]['name'] = []
        spotify_albums[album_uri]['uri'] = []
        tracks = sp.album_tracks(album_uri)  # pull data on album tracks
        for n in range(len(tracks['items'])):  # for each song track
            spotify_albums[album_uri]['album'].append(
                album_names[album_count])  # append album name tracked via album_count
            spotify_albums[album_uri]['track_number'].append(tracks['items'][n]['track_number'])
            spotify_albums[album_uri]['id'].append(tracks['items'][n]['id'])
            spotify_albums[album_uri]['name'].append(tracks['items'][n]['name'])
            spotify_albums[album_uri]['uri'].append(tracks['items'][n]['uri'])

    spotify_albums = {}
    album_count = 0
    for i in album_uris:  # each album
        albumSongs(i)
        album_count += 1  # Updates album count once all tracks have been added

    def audio_features(album):
        # Add new key-values to store audio features
        spotify_albums[album]['Acousticness'] = []
        spotify_albums[album]['Danceability'] = []
        spotify_albums[album]['Energy'] = []
        spotify_albums[album]['Instrumentalness'] = []
        spotify_albums[album]['Liveness'] = []
        spotify_albums[album]['Loudness'] = []
        spotify_albums[album]['Speechiness'] = []
        spotify_albums[album]['Tempo'] = []
        spotify_albums[album]['Valence'] = []
        spotify_albums[album]['Popularity'] = []

        for track in spotify_albums[album]['uri']:
            # pull audio features per track
            features = sp.audio_features(track)

            # Append to relevant key-value
            spotify_albums[album]['Acousticness'].append(features[0]['acousticness'])
            spotify_albums[album]['Danceability'].append(features[0]['danceability'])
            spotify_albums[album]['Energy'].append(features[0]['energy'])
            spotify_albums[album]['Instrumentalness'].append(features[0]['instrumentalness'])
            spotify_albums[album]['Liveness'].append(features[0]['liveness'])
            spotify_albums[album]['Loudness'].append(features[0]['loudness'])
            spotify_albums[album]['Speechiness'].append(features[0]['speechiness'])
            spotify_albums[album]['Tempo'].append(features[0]['tempo'])
            spotify_albums[album]['Valence'].append(features[0]['valence'])
            # popularity is stored elsewhere
            pop = sp.track(track)
            spotify_albums[album]['Popularity'].append(pop['popularity'])

    data_load_state = st.text('Loading data... This may take a minute.')
    request_count = 0
    bar = st.progress(request_count)

    for i in spotify_albums.keys():
        audio_features(i)
        request_count += 1
        bar.progress(request_count / len(spotify_albums))

    data_load_state.text('Loading data... Done!')

    dic_df = {'album': [],
              'track_number': [],
              'id': [],
              'name': [],
              'uri': [],
              'Acousticness': [],
              'Danceability': [],
              'Energy': [],
              'Instrumentalness': [],
              'Liveness': [],
              'Loudness': [],
              'Speechiness': [],
              'Tempo': [],
              'Valence': [],
              'Popularity': []}

    for album in spotify_albums:
        for feature in spotify_albums[album]:
            dic_df[feature].extend(spotify_albums[album][feature])

    df = pd.DataFrame.from_dict(dic_df)
    df['artist'] = artist

    end_time = time.time()  # to calculate the time it takes to process everything
    print(f"Timing: {end_time - begin_time:.0f}s.")

    return df.sort_values('Popularity', ascending=False).drop_duplicates('name').sort_index()
