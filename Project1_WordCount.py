# Get our post reader and open the xml file
from post_parser_record import PostParserRecord
#post_reader = PostParserRecord("data/Posts.xml")
post_reader = PostParserRecord("data/Posts_Small.xml")

# imports
import nltk
from nltk.corpus import stopwords
from nltk.corpus.reader.tagged import word_tokenize
import re, string
import csv
import matplotlib.pyplot as plt
from wordcloud import WordCloud
nltk.download('punkt')
nltk.download('stopwords')

def countPostWords():
    """
    This function counts all of the words in both the questions
    and answers. Keeps track of word count in word_dict.
    """
    print("Beginning to process questions...")

    # For each question
    for answer_id in post_reader.map_questions:
        # Get text
        text = (post_reader.map_questions[answer_id].title + " " + post_reader.map_questions[answer_id].body)
        # Remove punctuations, Make lowercase
        token_words = re.sub("<.*?>|\\n|&quot;", " ", text.lower())
        # Tokenize words into list
        token_words = word_tokenize(token_words.translate(str.maketrans('', '', string.punctuation)))
        # Now go through all the words and add to the dictionary
        for word in token_words:
            word.replace('\'', '')
            if word in word_dict:
                word_dict[word] = word_dict[word] + 1
            else:
                word_dict[word] = 1
    
    print("Beginning to process answers...")

    # For each answer
    for answer_id in post_reader.map_just_answers:
        # Get text
        text = (post_reader.map_just_answers[answer_id].body)
        # Remove punctuations, Make lowercase
        token_words = re.sub("<.*?>|\\n|&quot;", " ", text.lower())
        # Tokenize words into list
        token_words = word_tokenize(token_words.translate(str.maketrans('', '', string.punctuation)))
        # Now go through all the words and add to the dictionary
        for word in token_words:
            word.replace('\'', '')
            if word in word_dict:
                word_dict[word] = word_dict[word] + 1
            else:
                word_dict[word] = 1

# To start, build our collections without removing stop words.
# Build a word dict of vocab : count
word_dict = {}
countPostWords()
print("Finished processing!")
# Sort dictionary
sorted_word_dict = dict(sorted(word_dict.items(), key=lambda item: item[1], reverse=True))
# Save results in a file for easier data usage:
with open("data/P1_WordCount.csv", 'w', encoding ="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=['Word', 'Count'], delimiter='\t')
    writer.writeheader()
    for word in word_dict:
        writer.writerow({'Word': word, 'Count': word_dict[word]})
print("File P1_WordCount.csv Finished")

word_dict_stopwords = {}
# Remove stop words from the dictionary
for word, count in sorted_word_dict.items():
    if word not in stopwords.words('english'):
        word_dict_stopwords[word] = count

with open("data/P1_WordCount_StopWords.csv", 'w', encoding ="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=['Word', 'Count'], delimiter='\t')
    writer.writeheader()
    for word in word_dict_stopwords:
        writer.writerow({'Word': word, 'Count': word_dict_stopwords[word]})

print("File P1_WordCount_StopWords.csv Finished")