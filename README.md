# genre_lyrycs_map
Small fun project for generating a word cloud for music genre lyrics.
## Requirements:
	*Python 3
	*requests (Py module, can get with pip)
	*WordCloud (Py module, can get with pip)
	*matplotlib (Py module, can get with pip)
## How to run:
	First run the _retrieve_lyrics_data.py_ script with Python and provide wikidata entity ID for the genre for getting lyrics and saving them to file.
	Then if there are lyrics file present you can run _generate_word_map.py_ with Python provide wikidata entity ID for the genre to draw the word cloud.
