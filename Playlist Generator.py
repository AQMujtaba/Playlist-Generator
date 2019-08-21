#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
from bs4 import BeautifulSoup
import spotipy
import spotipy.util as util
import os
import sys
import json


# In[ ]:


def gather_playlist():
    with requests.Session() as session:
        url = input("Link to playlist: ")
        response = session.get(url, allow_redirects=True)

        source = BeautifulSoup(response.text, 'html.parser')
        tracklist = []
        artists = []

        # find the title of all songs from playlist
        for node in source.find_all('div', class_='track-title'):
            tracklist.append(''.join(node.find_all(text=True)))

        # find the artists for all songs from the playlist
        for node in source.find_all('td', class_='artist-col fade-out'):
            artists.append(''.join(node.find_all(text=True)))

        # append the artist and track data to form a search query
        TRACK_COUNT = len(tracklist)
        for track in range(TRACK_COUNT):
            tracklist[track] += " " + (artists[track])
            # checks to replace characters that can tend to result in mismatch
            if ("feat." in tracklist[track]):
                tracklist[track] = tracklist[track].replace("feat. ", "")
            if ("&" in tracklist[track]):
                tracklist[track] = tracklist[track].replace("& ", "")
                
        print("Adding following songs:\n")
        print(*tracklist, sep='\n')
        print("\n")

    return tracklist


# In[ ]:


def create_playlist(username, tracklist, client):
    playlist_name = input("Enter a playlist name: ")
    
    try:
        playlist = client.user_playlist_create(username, playlist_name)
        playlist_id = playlist['id']
    except Exception as e:
        print("Couldn't create playlist")
        print(e)
    
    TRACK_COUNT = len(tracklist)
    track_uris = [] # URIs needed to add tracks
    
    # gather all URIs for songs found
    for track in range(TRACK_COUNT):
        results = client.search(tracklist[track], 1, 0, 'track')
        
        # add URI of first track found (assuming best match)
        try:
            uri = results['tracks']['items'][0]['uri']
            track_uris.append(uri)
        except:
            print("Couldn't find: " + tracklist[track])
  
    # try adding all URIs to created playlist
    try:
        client.user_playlist_add_tracks(username, playlist_id, track_uris)
        print("All tracks added")
    except:
        print("Couldn't add all tracks")


# In[ ]:


def main():
    USERNAME = os.environ.get("SPOTIPY_USER")
    scope = ("user-top-read playlist-modify-private "
             "playlist-modify-public playlist-read-private")

    try:
        token = util.prompt_for_user_token(USERNAME, scope)
    except:
        os.remove(f".cache-{USERNAME}")
        token = util.prompt_for_user_token(USERNAME, scope)

    client = spotipy.Spotify(auth=token)
    
    tracklist = gather_playlist()
    create_playlist(USERNAME, tracklist, client)


# In[ ]:


if __name__ == "__main__":
    main()

