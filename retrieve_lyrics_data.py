import requests
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from os import path
import time
import sys

HEADERS = { 'User-Agent': 'Genre Lyrics Word Cloud Bot/1.0 (https://github.com/vehiginters/genre_lyrycs_map, vehiginters@gmail.com)'}

"""
SELECT ?SongLabel ?BandLabel
WHERE
{
  ?Song wdt:P31 wd:Q134556.
  ?Song wdt:P175 ?Band.
  {
    SELECT ?Band (SUM(?Listeners) AS ?TotalListeners)
        WHERE
        {
          ?BandSubClass wdt:P279* wd:Q215380. # As different bands tend to be categorized in different subclasses of "musical group" get all subclasses of "musical group"
          ?Band wdt:P31 ?BandSubClass.
          ?Band wdt:P136 wd:Q38848.
          ?Band p:P2397 ?YoutubeChannel.
          ?YoutubeChannel pq:P5436 ?Listeners.
          ?YoutubeChannel pq:P1552 ?ChannelType.
          VALUES ?ChannelType {wd:Q72112388 wd:Q72108022}
        }
        GROUP BY ?Band
        ORDER BY DESC (?TotalListeners)
        LIMIT 10
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
}
ORDER BY ?BandLabel
"""

def get_song_lyrics(artist, song):
	time.sleep(3) # Sleep a bit between requests, not to get locked out
	print("Retriving lyrics for {} song {}".format(artist, song))
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
		print("ChartLyrics bad reponse - {}".format(response.status_code))


def format_lyrics(lyrics):
	lyrics = lyrics.translate({ord(i): None for i in ',.!?'})
	lyrics = lyrics.lower()
	lyrics_list = lyrics.split(" ")
	filter_words = ["about", "after", "all", "also", "an", "and", "another", "any", "are", "as", "at", "be", "because", "been", "before", "being", "between", "both", "but", "by",
	                "came", "can", "come", "could", "did", "do", "does", "each", "else", "for", "from", "get", "got", "had", "has", "have", "he", "her", "here", "him", "himself",
	                "his", "how", "if", "in", "into", "is", "it", "its", "just", "like", "make", "many", "me", "might", "more", "most", "much", "must", "my", "never", "no", "now",
	                "of", "on", "only", "or", "other", "our", "out", "over", "re", "said", "same", "see", "should", "since", "so", "some", "still", "such", "take", "than", "that",
	                "the", "their", "them", "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "up", "use", "very", "want", "was", "way", "we", "well",
	                "were", "what", "when", "where", "which", "while", "who", "will", "with", "would", "you", "your"]
	return ' '.join(filter(lambda val: val not in filter_words, lyrics_list))

def save_lyrics(lyrics, genre_id):
	file_name = "{}.txt".format(genre_id)
	if path.exists(file_name):
		f = open(file_name, "a")
		f.write(" " + lyrics)
		f.close()
	else:
		print("Creating new file for saving lyrics")
		f = open(file_name, "w")
		f.write(lyrics)
		f.close()

if __name__ == "__main__":
	lyrics = get_song_lyrics("Disturbed", "Decadence")
	if not lyrics:
		print("No lyrics found for {} song {}".format(artist, song))
		# return
		sys.exit()
	formatted = format_lyrics(lyrics)
	save_lyrics(formatted, "Q38848")
	print("Lyrics saved to file")
