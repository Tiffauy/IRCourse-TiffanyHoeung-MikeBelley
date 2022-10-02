# Get our post reader and open the xml file
from codecs import utf_8_encode
from post_parser_record import PostParserRecord
post_reader = PostParserRecord("data/Posts.xml")
#post_reader = PostParserRecord("data/Posts_Small.xml")

# imports
import nltk
from nltk.corpus import stopwords
from nltk.corpus.reader.tagged import word_tokenize
import re, string
import csv
import matplotlib.pyplot as plt
from wordcloud import WordCloud
#nltk.download('punkt')
#nltk.download('stopwords')

word_dict = {}

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
            if word in word_dict:
                docs = word_dict[word]
                if answer_id not in docs:
                    docs.add(answer_id)
                word_dict[word] = docs
            else:
                docs = {answer_id}
                word_dict[word] = docs
    
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
            if word in word_dict:
                docs = word_dict[word]
                if answer_id not in docs:
                    docs.add(answer_id)
                word_dict[word] = docs
            else:
                docs = {answer_id}
                word_dict[word] = docs

def saveInvertedIndex():
    print("Saving data to tsv...")
    keys = ['Word', 'Documents']

    with open("data/InvertedIndex.tsv", "w", encoding="utf-8", newline='') as f:
        dict_writer = csv.DictWriter(f, keys, delimiter='\t')
        dict_writer.writeheader()
        for word in word_dict:
            dict_writer.writerow({"Word": word, "Documents": word_dict[word]})

def processTSV():
    with open("data/InvertedIndex.tsv") as f:
        tsv_file = csv.reader(f, delimiter="\t")
        next(tsv_file)
        for line in tsv_file:
            word_dict[line[0]] = set(line[1].strip('}{').split(', '))

# Ask user if they want to reprocess posts
validInput = False
userInput = input("First time parsing the posts? (Y/N): ")
while validInput == False:
    if(userInput[0] == 'Y' or userInput[0] == 'y'):
        countPostWords()
        saveInvertedIndex()
        validInput = True
    elif(userInput[0] == 'N' or userInput[0] == 'n'):
        processTSV()
        validInput = True
    else:
        print("Invalid input. Input Y or N")
        userInput = input("Regenerate Inverted Index? (Y/N): ")

# At this point, we have inverted index from reading through the file or processing TSV
# First we need to get our query from the user
hasAnotherQuery = True
while hasAnotherQuery:
    userInput = input("Input your query: ")
    parsed_query = userInput.split()
    boolean_op = -1 # Used to keep track of OR and AND. 0 = OR, 1 = AND, -1 = No value atm
    results = {}
    for word in parsed_query:
        if(word != "OR" and word != "AND"):
            word = word.lower()
            docs = word_dict.get(word)
            if(boolean_op == -1): # FIRST WORD
                results = docs
            elif(boolean_op == 0): # OR
                if(type(docs) == set):
                    results = results | docs
            elif(boolean_op == 1): # AND
                if(type(docs) == set):
                    results = results & docs
                else:
                    results = docs
        elif(word == "OR"):
            boolean_op = 0
        elif(word == "AND"):
            boolean_op = 1
    # if results is not a set, set it to an empty set; type will be NoneType
    if(type(results) != set):
        results = {}
    results = sorted(list(results))

    print("The top 50 results for your query are: ")
    print(results[:50])

    # Ask user if they want another query
    userInput = input("Would you like to make another query? (Y/N): ")
    validInput = False
    while validInput == False:
        if(userInput[0] == 'Y' or userInput[0] == 'y'):
            hasAnotherQuery = True
            validInput = True
        elif(userInput[0] == 'N' or userInput[0] == 'n'):
            hasAnotherQuery = False
            validInput = True
        else:
            print("Invalid input. Input Y or N")
            userInput = input("Regenerate Inverted Index? (Y/N): ")