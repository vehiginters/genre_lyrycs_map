import matplotlib.pyplot as plt
from wordcloud import WordCloud
from os import path
import sys

def read_lyrics(genre_id):
	file_name = "{}.txt".format(genre_id)
	if path.exists(file_name):
		f = open(file_name, "r")
		return f.read()

if __name__ == "__main__":
	lyrics = read_lyrics("Q38848")
	if not lyrics:
		print("No lyrics found")
		sys.exit()
	print("Drawing word map...")
	word_cloud = WordCloud(collocations = False, background_color = 'white').generate(lyrics)
	plt.imshow(word_cloud, interpolation='bilinear')
	plt.axis("off")
	plt.show()
