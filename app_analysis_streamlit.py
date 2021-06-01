import streamlit as st
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from df_spotipy import *

# PAGE TEMPLATE (title, icon, layout e sidebar)
st.set_page_config(page_title="Analysis", page_icon=":waning_crescent_moon:", layout='centered',
                   initial_sidebar_state='expanded')

# GRAPHS TEMPLATE
pio.templates.default = 'none'



###########
## TITLE ##
###########

st.header('Spotify Songs Analysis App (working title)')
st.write("Github: cyberfunker")

st.write("")



###############
## DATAFRAME ##
###############

search = st.text_input("Pick an artist: ", "Loona")

if not search:
    search = "Loona"

st.text("PS: if none, it'll show an artist of my choice.")

st.text("")

raw_data = busca_artista(search)  # SEARCH ARTIST DATA ON THE SPOTIFY API (see app_spotipy.py)

artista = raw_data.iloc[0]["artist"]

st.markdown(f"#### Artist: {artista}")
st.write("___")

dados = raw_data[["album", "name", "Acousticness", "Danceability", "Energy", "Instrumentalness", "Liveness", "Loudness",
                  "Speechiness", "Valence", "Tempo", "Popularity"]]

atributos = ["Acousticness", "Danceability", "Energy", "Instrumentalness", "Liveness", "Loudness", "Speechiness",
             "Valence", "Tempo", "Popularity"]

atributos_01 = ["Acousticness", "Danceability", "Energy", "Instrumentalness", "Liveness", "Speechiness", "Valence"]


def filter_column(df, column):  # GROUP THE DATAFRAME BY GIVEN COLUMN (MEAN)
    return df.groupby([column]).mean()


df_album = filter_column(dados, "album")
df_name = filter_column(dados, "name")



#############
## SIDEBAR ##
#############

filtro_album = dados["album"].sort_values().unique()
filtro_musica = dados["name"].sort_values().unique()

st.sidebar.subheader("Select filters:")
st.sidebar.text("(optional)")

album_check = st.sidebar.checkbox('By Album')
musica_check = st.sidebar.checkbox('By Tracks')


if album_check and not musica_check:  
    album_filter = st.sidebar.multiselect(
        'Choose Albums:',
        filtro_album)

    if album_filter and len(album_filter) <= 10:

        df_name_album = filter_column(dados[dados["album"].isin(album_filter)], "name")
        df_name_list = df_name_album.index.tolist()

        # POPULARITY RANK
        col1, col2 = st.beta_columns(2)
        col1.subheader("Top 10 tracks")
        col1.table(df_name_album.sort_values("Popularity", ascending=False)["Popularity"].head(10))

        st.write("___")

        st.subheader("Album Features")
        fig1 = go.Figure()
        for i in album_filter:
            fig1.add_trace(go.Scatterpolar(r=df_album.loc[i, atributos_01], theta=atributos_01, fill="toself", name=i,
                                           mode="markers", marker_size=4,
                                           marker_color=px.colors.sequential.Viridis[album_filter.index(i)]))

        st.write(fig1, "___")

        st.subheader("Feature comparison between album tracks")
        st.write(f"Selected albums: {str(album_filter)[1:-1]}")
        atributo = st.selectbox("Choose feature: ", atributos, index=2)
        st.write(f"Mean: {df_name_album[atributo].mean().round(decimals=2)}")
        fig2 = px.bar(df_name_album, x=df_name_list, y=atributo, color="Popularity",
                      color_continuous_scale=px.colors.sequential.Sunsetdark, labels={'x': ''})

        st.write(fig2, "___")

        st.subheader("Relationship between features")

        col5, col6 = st.beta_columns(2)

        atributo_y = col5.selectbox("Select y axis feature: ", atributos, index=2)
        atributo_x = col6.selectbox("Select x axis feature: ", atributos, index=7)

        st.write("")

        st.markdown("#### By track")
        fig3 = px.scatter(df_name_album, x=atributo_x, y=atributo_y, color="Popularity",
                          color_continuous_scale=px.colors.sequential.Sunsetdark)
        st.write(fig3)

    else:
        st.markdown("##### Choose the albums in the sidebar. (máx. 10)")

    st.write("___")

if musica_check and not album_check:
    song_filter = st.sidebar.multiselect('Choose Tracks: ', filtro_musica)

    if song_filter:

        df_name_track = df_name[df_name.index.isin(song_filter)]
        df_name_list = df_name_track.index.tolist()

        # POPULARITY RANK

        col1, col2 = st.beta_columns(2)
        col1.subheader("Popularity Rank")
        col1.table(df_name_track.sort_values("Popularity", ascending=False)["Popularity"].head(10))

        st.write("___")

        # FEATURES

        st.subheader("Tracks Features")

        fig4 = make_subplots(rows=1, cols=2, subplot_titles=("Acousticness", "Danceability"))
        fig5 = make_subplots(rows=1, cols=2, subplot_titles=("Energy", "Valence"))
        fig6 = make_subplots(rows=1, cols=2, subplot_titles=("Tempo", "Loudness"))
        fig7 = make_subplots(rows=1, cols=2, subplot_titles=("Instrumentalness", "Liveness"))

        fig4.add_trace(go.Bar(x=df_name_list, y=df_name_track["Acousticness"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=1, )

        fig4.add_trace(go.Bar(x=df_name_list, y=df_name_track["Danceability"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=2)

        fig5.add_trace(go.Bar(x=df_name_list, y=df_name_track["Energy"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=1)

        fig5.add_trace(go.Bar(x=df_name_list, y=df_name_track["Valence"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=2)

        fig6.add_trace(go.Bar(x=df_name_list, y=df_name_track["Tempo"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=1)

        fig6.add_trace(go.Bar(x=df_name_list, y=df_name_track["Loudness"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=2)

        fig7.add_trace(go.Bar(x=df_name_list, y=df_name_track["Instrumentalness"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=1)

        fig7.add_trace(go.Bar(x=df_name_list, y=df_name_track["Liveness"],
                              marker=dict(color=df_name_track["Popularity"], coloraxis="coloraxis")),
                       row=1, col=2)

        fig4.update_layout(coloraxis=dict(colorscale='Sunsetdark'), showlegend=False)
        fig5.update_layout(coloraxis=dict(colorscale='Sunsetdark'), showlegend=False)
        fig6.update_layout(coloraxis=dict(colorscale='Sunsetdark'), showlegend=False)
        fig7.update_layout(coloraxis=dict(colorscale='Sunsetdark'), showlegend=False)

        st.write(fig4, fig5, fig6, fig7)

        st.write("___")



    else:
        st.markdown("##### Choose the tracks in the sidebar.")

if (not album_check and not musica_check) or (album_check and musica_check):
    col1, col2 = st.beta_columns(2)
    col1.subheader("Top 10 tracks")
    col1.table(df_name.sort_values("Popularity", ascending=False)["Popularity"].head(10))
    col2.subheader("Top 10 albums")
    col2.table(df_album.sort_values("Popularity", ascending=False)["Popularity"].astype(int).head(10))

    st.write("___")

    st.subheader("Feature comparison between albums")
    atributo = st.selectbox("Select feature:", atributos, index=2)
    st.write(f"Mean: {df_album[atributo].mean().round(decimals=2)}")
    fig8 = px.bar(df_album, x=filtro_album, y=atributo, color="Popularity",
                  color_continuous_scale=px.colors.sequential.Sunsetdark, labels={'x': ''})
    st.write(fig8)

    st.write("___")

    st.subheader("Relationship between features")

    col3, col4 = st.beta_columns(2)

    atributo_y = col3.selectbox("Select y axis feature: ", atributos, index=2)
    atributo_x = col4.selectbox("Select x axis feature: ", atributos, index=7)

    st.write("")

    st.markdown("#### By album")
    fig9 = px.scatter(df_album, x=atributo_x, y=atributo_y, color="Popularity",
                      color_continuous_scale=px.colors.sequential.Sunsetdark, hover_data=[df_album.index])
    st.write(fig9)

    st.markdown("#### By track")
    fig10 = px.scatter(df_name, x=atributo_x, y=atributo_y, color="Popularity",
                       color_continuous_scale=px.colors.sequential.Sunsetdark, hover_data=[df_name.index])
    st.write(fig10)

    st.write("___")

    if st.checkbox("Show high tempo tracks (150 BPM or faster)"):
        bpm150 = df_name['Tempo'] >= 150
        df_150 = df_name[bpm150]
        st.write(df_150.sort_values("Tempo", ascending=False)["Tempo"].astype(int))

    st.write("___")

st.sidebar.write("___")

st.sidebar.header('Features Description:')

st.sidebar.subheader("Acousticness")
st.sidebar.write(
    "A confidence measure from 0.0 to 1.0 of whether the track is acoustic. 1.0 represents high confidence the track is acoustic.")

st.sidebar.subheader("Danceability")
st.sidebar.write(
    "Danceability describes how suitable a track is for dancing based on a combination of musical elements including tempo, rhythm stability, beat strength, and overall regularity. A value of 0.0 is least danceable and 1.0 is most danceable.")

st.sidebar.subheader("Energy")
st.sidebar.write(
    "Energy is a measure from 0.0 to 1.0 and represents a perceptual measure of intensity and activity. Typically, energetic tracks feel fast, loud, and noisy. For example, death metal has high energy, while a Bach prelude scores low on the scale. Perceptual features contributing to this attribute include dynamic range, perceived loudness, timbre, onset rate, and general entropy.")

st.sidebar.subheader("Instrumentalness")
st.sidebar.write(
    'Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.')

st.sidebar.subheader("Liveness")
st.sidebar.write(
    "Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.")

st.sidebar.subheader("Loudness")
st.sidebar.write(
    "The overall loudness of a track in decibels (dB). Loudness values are averaged across the entire track and are useful for comparing relative loudness of tracks. Loudness is the quality of a sound that is the primary psychological correlate of physical strength (amplitude). Values typical range between -60 and 0 db.")

st.sidebar.subheader("Speechiness")
st.sidebar.write(
    "Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.")

st.sidebar.subheader("Valence")
st.sidebar.write(
    "A measure from 0.0 to 1.0 describing the musical positiveness conveyed by a track. Tracks with high valence sound more positive (e.g. happy, cheerful, euphoric), while tracks with low valence sound more negative (e.g. sad, depressed, angry). ")

st.sidebar.subheader("Tempo")
st.sidebar.write(
    "The overall estimated tempo of a track in beats per minute (BPM). In musical terminology, tempo is the speed or pace of a given piece and derives directly from the average beat duration.")

st.sidebar.write("___")