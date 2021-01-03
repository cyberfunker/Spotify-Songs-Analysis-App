import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import time
import numpy as np
import pandas as pd
import streamlit as st
import config


client_credentials_manager = SpotifyClientCredentials(client_id=config.id, client_secret=config.secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager) # ACESSA A API

@st.cache(suppress_st_warning=True)
def busca_artista(busca):
  
    result = sp.search(busca) # FAZ A BUSCA E RETORNA INFO
    result["tracks"]["items"][0]["artists"]


    artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
    artist_uri


    #Pull all of the artist's albums
    sp_albums = sp.artist_albums(artist_uri)
    #Store artist's albums' names' and uris in separate lists
    album_names = []
    album_uris = []
    for i in range(len(sp_albums['items'])):
        album_names.append(sp_albums['items'][i]['name'])
        album_uris.append(sp_albums['items'][i]['uri'])
        
    album_names
    album_uris
    #Keep names and uris in same order to keep track of duplicate albums


    def albumSongs(uri):
        album = uri #assign album uri to a_name
        spotify_albums[album] = {} #Creates dictionary for that specific album
        #Create keys-values of empty lists inside nested dictionary for album
        spotify_albums[album]['album'] = [] #create empty list
        spotify_albums[album]['track_number'] = []
        spotify_albums[album]['id'] = []
        spotify_albums[album]['name'] = []
        spotify_albums[album]['uri'] = []
        tracks = sp.album_tracks(album) #pull data on album tracks
        for n in range(len(tracks['items'])): #for each song track
                spotify_albums[album]['album'].append(album_names[album_count]) #append album name tracked via album_count
                spotify_albums[album]['track_number'].append(tracks['items'][n]['track_number'])
                spotify_albums[album]['id'].append(tracks['items'][n]['id'])
                spotify_albums[album]['name'].append(tracks['items'][n]['name'])
                spotify_albums[album]['uri'].append(tracks['items'][n]['uri'])


    spotify_albums = {}
    album_count = 0
    for i in album_uris: #each album
        albumSongs(i)
        print("Album " + str(album_names[album_count]) + " songs has been added to spotify_albums dictionary")
        album_count+=1 #Updates album count once all tracks have been added


    def audio_features(album):
        #Add new key-values to store audio features
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
        #create a track counter
        track_count = 0
        for track in spotify_albums[album]['uri']:
            #pull audio features per track
            features = sp.audio_features(track)
            
            #Append to relevant key-value
            spotify_albums[album]['Acousticness'].append(features[0]['acousticness'])
            spotify_albums[album]['Danceability'].append(features[0]['danceability'])
            spotify_albums[album]['Energy'].append(features[0]['energy'])
            spotify_albums[album]['Instrumentalness'].append(features[0]['instrumentalness'])
            spotify_albums[album]['Liveness'].append(features[0]['liveness'])
            spotify_albums[album]['Loudness'].append(features[0]['loudness'])
            spotify_albums[album]['Speechiness'].append(features[0]['speechiness'])
            spotify_albums[album]['Tempo'].append(features[0]['tempo'])
            spotify_albums[album]['Valence'].append(features[0]['valence'])
            #popularity is stored elsewhere
            pop = sp.track(track)
            spotify_albums[album]['Popularity'].append(pop['popularity'])
            track_count+=1


    data_load_state = st.text('Loading data...')
    start_time = time.time()
    request_count = 0
    bar = st.progress(request_count)
    for i in spotify_albums:
        audio_features(i)
        request_count+=1
        bar.progress(request_count/len(spotify_albums))
        if request_count % 5 == 0:
            print(str(request_count) + " playlists completed")
            time.sleep(2)
            print('Loop #: {}'.format(request_count))
            print('Elapsed Time: {} seconds'.format(time.time() - start_time))

    data_load_state.text('Loading data... Done!')

    dic_df = {}
    dic_df['album'] = []
    dic_df['track_number'] = []
    dic_df['id'] = []
    dic_df['name'] = []
    dic_df['uri'] = []
    dic_df['Acousticness'] = []
    dic_df['Danceability'] = []
    dic_df['Energy'] = []
    dic_df['Instrumentalness'] = []
    dic_df['Liveness'] = []
    dic_df['Loudness'] = []
    dic_df['Speechiness'] = []
    dic_df['Tempo'] = []
    dic_df['Valence'] = []
    dic_df['Popularity'] = []
    for album in spotify_albums: 
        for feature in spotify_albums[album]:
            dic_df[feature].extend(spotify_albums[album][feature])
            

    df = pd.DataFrame.from_dict(dic_df)
    df['artist'] = busca


    return df.sort_values('Popularity', ascending=False).drop_duplicates('name').sort_index()