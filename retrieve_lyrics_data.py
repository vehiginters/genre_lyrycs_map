import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from os import path
import time
import sys
import json

HEADERS = { 'User-Agent': 'Genre Lyrics Word Cloud Bot/1.0 (https://github.com/vehiginters/genre_lyrycs_map, vehiginters@gmail.com)'}
GENRE = "Q484641"
BAND_LIMIT = 10
SONGS_PER_BAND = 5

def get_list_of_artists_and_songs(genre_id):
    url = 'https://query.wikidata.org/sparql'
    query = '''
        SELECT ?songLabel ?bandLabel ?TotalListeners
        WHERE
        {{
          ?song wdt:P31 wd:Q134556.
          ?song wdt:P175 ?band.
          {{
        SELECT ?band (SUM(?YoutubeListeners) + SUM(?SpotifyListeners) AS ?TotalListeners)
        WHERE
        {{
          ?BandSubClass wdt:P279* wd:Q215380. # As different bands tend to be categorized in different subclasses of "musical group" get all subclasses of "musical group"
          ?band wdt:P31 ?BandSubClass.
          ?band wdt:P136 {genreId}.
          OPTIONAL
          {{
            ?band p:P2397 ?YoutubeChannel.
            ?YoutubeChannel pq:P5436 ?YoutubeListeners.
            ?YoutubeChannel pq:P1552 ?ChannelType.
            VALUES ?ChannelType {{ wd:Q72112388 wd:Q72108022 }}
          }}
          OPTIONAL
          {{
            ?band p:P1902 ?SpotifyChannel.
            ?SpotifyChannel pq:P5436 ?SpotifyListeners.
          }}
        }}
        GROUP BY ?band
        ORDER BY DESC (?TotalListeners)
        LIMIT {bandLimit}
          }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        ORDER BY DESC (?TotalListeners) ASC (?bandLabel)
    '''.format(genreId = "wd:" + genre_id, bandLimit = BAND_LIMIT)
    body = {'query': query,
            'format': 'json',}
    response = requests.post(url, headers = HEADERS, data = body)
    if response.ok:
        return json.loads(response.text)['results']['bindings']
    else:
        print("WikiData returned response code - {}, reason - {}".format(response.status_code, response.reason))
        return {}

def get_song_lyrics(artist, song):
    time.sleep(3) # Sleep a bit between requests, not to get locked out
    URL = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist={}&song={}".format(artist, song)
    response = requests.get(url = URL, headers = HEADERS)
    if response.ok:
        root = ET.fromstring(response.text)
        for child in root:
            if child.tag == "{http://api.chartlyrics.com/}Lyric":
                return child.text
    elif response.status_code == 429 or response.status_code == 503 : # To many requests in the last minute, let's wait some time till we make a new one
        sleepTime = 5
        if "Retry-After" in response.headers:
            sleepTime = int(response.headers["Retry-After"])
        print("ChartLyrics Query Limit reached. Retrying after {}s".format(sleepTime))
        time.sleep(sleepTime+1)
    else:
        print("ChartLyrics bad reponse - {}, reason - {}".format(response.status_code, response.reason))


def format_lyrics(lyrics):
    lyrics = lyrics.translate({ord(i): None for i in ',.!?()[]{}1234567890'})
    lyrics = lyrics.lower()
    lyrics_list = lyrics.split(" ")
    filter_words = ["about", "after", "all", "also", "an", "and", "another", "any", "are", "as", "at", "be", "because", "been", "before", "being", "between", "both", "but", "by",
                    "came", "can", "come", "could", "did", "do", "does", "each", "else", "for", "from", "get", "got", "had", "has", "have", "he", "her", "here", "him", "himself",
                    "his", "how", "if", "in", "into", "is", "it", "its", "just", "like", "make", "many", "me", "might", "more", "most", "much", "must", "my", "never", "no", "now",
                    "of", "on", "only", "or", "other", "our", "out", "over", "re", "said", "same", "see", "should", "since", "so", "some", "still", "such", "take", "than", "that",
                    "the", "their", "them", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "up", "use", "very", "want", "was", "way", "we", "well",
                    "were", "what", "when", "where", "which", "while", "who", "will", "with", "would", "you", "your", "chorus", "repeat"]
    return ' '.join(filter(lambda val: val not in filter_words, lyrics_list))

def save_lyrics(lyrics, genre_id):
    file_name = "{}.txt".format(genre_id)
    if path.exists(file_name):
        f = open(file_name, "a", encoding="utf-8")
        f.write(" " + lyrics)
        f.close()
    else:
        print("Creating new file for saving lyrics")
        f = open(file_name, "w", encoding="utf-8")
        f.write(lyrics)
        f.close()

if __name__ == "__main__":
    print("Starting lyrics retrieval for {} bands with {} songs per band".format(BAND_LIMIT, SONGS_PER_BAND))
    artists_and_songs = get_list_of_artists_and_songs(GENRE)
    songs_found = 0
    last_band = ""
    for i in artists_and_songs:
        band = i['bandLabel']['value']
        song = i['songLabel']['value']
        if band == last_band and songs_found >= SONGS_PER_BAND: # Don't take too many songs from one artist
            continue
        if band != last_band: # New band found, reset counter
            songs_found = 0

        lyrics = get_song_lyrics(band,song)
        if lyrics:
            print("Got lyrics for [{}] [{}]".format(band,song))
            songs_found += 1
            formatted = format_lyrics(lyrics)
            save_lyrics(formatted, GENRE)
        else:
            print("No lyrics found for [{}] [{}]".format(band,song))
        last_band = band
