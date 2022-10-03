# Imports
from codecs import utf_8_encode
from typing import Dict
from post_parser_record import PostParserRecord
post_reader = PostParserRecord("data/Posts.xml")            # Interchangeable with line 5
#post_reader = PostParserRecord("data/Posts_Small.xml")     # Interchangeable with line 4
import sys
import csv
import time
from nltk.corpus import stopwords
from nltk.corpus.reader.tagged import word_tokenize
import re, string
from collections import Counter
from itertools import islice
maxInt = sys.maxsize
# Used to increase max csv file in case we are parsing from TSV
while True:
    # decrease the maxInt value by factor 10 
    # as long as the OverflowError occurs.
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

def createInvertedIndex():
    """
    This function counts all of the words in both the questions
    and answers. Keeps track of documents with their word counts
    in a dictionary to their term. vocab : {doc:count, doc:count}
    """
    print("Processing questions...")
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
            if word not in stopwords.words('english'):
                if word in word_dict:
                    docs = word_dict[word]
                    if answer_id not in docs:
                        docs.update({answer_id:1})
                    else:
                        docs[answer_id] = docs[answer_id]+1
                    word_dict[word] = docs
                else:
                    docs = {answer_id:1}
                    word_dict[word] = docs
    
    print("Processing answers...")
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
            if word not in stopwords.words('english'):
                if word in word_dict:
                    docs = word_dict[word]
                    if answer_id not in docs:
                        docs.update({answer_id:1})
                    else:
                        docs[answer_id] = docs[answer_id]+1
                    word_dict[word] = docs
                else:
                    docs = {answer_id:1}
                    word_dict[word] = docs

def saveInvertedIndex():
    """
    This function saves word_dict into a TSV file and
    saves it to /data.
    """
    print("Saving data to tsv...")
    keys = ['Word', 'Documents']

    with open("data/InvertedIndexCounts.tsv", "w", encoding="utf-8", newline='') as f:
        dict_writer = csv.DictWriter(f, keys, delimiter='\t')
        dict_writer.writeheader()
        for word in word_dict:
            dict_writer.writerow({"Word": word, "Documents": str(word_dict[word])})

def processTSV():
    """
    processTSV() will open the TSV file at data/InvertedIndex.tsv
    and parse it into word_dict as {words : {docs}}.
    """
    with open("data/InvertedIndexCounts.tsv", encoding="utf-8") as f:
        tsv_file = csv.reader(f, delimiter="\t")
        next(tsv_file)
        for line in tsv_file:
            word_dict[line[0]] = eval(line[1])

def processQueryWord(word, results):
    """
    This function looks for word in the word_dict and combines
    it with our current set of results, then removes any documents
    that don't have both words.
    """
    # First, combine the dictionaries for word & results
    docs = word_dict.get(word)
    if(type(docs) == dict):
        combined_dic = (Counter(results) + Counter(word_dict.get(word)))
        combined_dic = {k: v for k, v in combined_dic.items() if k in results and k in word_dict.get(word)}
        return dict(combined_dic)
    else: # there are no documents for our word, return an empty dictionary
        return dict()


# START:
word_dict = {}
validInput = False

# Ask user if they want to reprocess posts; alternative is read from TSV
userInput = input("First time parsing the posts? (Y/N): ")
while validInput == False: 
    if(userInput[0].upper() == 'Y'):
        time_start = time.time()
        createInvertedIndex()       # Generates inverted index with count from Posts.xml
        time_end = time.time()
        print(f'Processing posts took %.2f s' % (time_end - time_start))
        saveInvertedIndex()         # Saves inverted index in TSV form
        validInput = True
    elif(userInput[0].upper() == 'N'):
        time_start = time.time()
        processTSV()                # Creates the inverted index from the TSV
        time_end = time.time()
        print(f'Processing posts took %.2f s' % (time_end - time_start))
        validInput = True
    else:
        print("Invalid input. Input Y or N")
        userInput = input("First time parsing the posts? (Y/N): ")

# Get the query from the user
vocab_to_doc = {} # Delete for final submission
hasAnotherQuery = True
while hasAnotherQuery:
    userInput = input("Input your query: ")
    parsed_query = userInput.split()
    results = [] 
    time_start = time.time()
    for word in parsed_query:
        word = word.lower()
        if word == parsed_query[0]:
            results = word_dict.get(word)
            if(type(results) != dict): # There are no documents for the word ; return empty dic
                results = dict()
        else:
            results = processQueryWord(word, results)
    results = dict(islice(sorted(results.items(), key=lambda item: item[1], reverse=True), 50)) # Get our documents and sort them
    print(f"The top %d results for your query are: " % len(results))
    print(results)
    time_end = time.time()
    print(f'Retrieving the index took %.2f ms' % ((time_end - time_start)*1000))

    vocab_to_doc[userInput] = list(results.keys())[:20] # Delete for final submission

    # Ask user if they want another query
    userInput = input("Would you like to make another query? (Y/N): ")
    validInput = False
    while validInput == False:
        if(userInput[0].upper() == 'Y'):
            hasAnotherQuery = True
            validInput = True
        elif(userInput[0].upper() == 'N'):
            print("QUERY\t\tDOCUMENTS") # Delete for final submission
            for query in vocab_to_doc: # Delete for final submission
                print(str(query) + ": \t\t" + str(vocab_to_doc[query])) # Delete for final submission
            hasAnotherQuery = False
            validInput = True
        else:
            print("Invalid input. Input Y or N")
            userInput = input("Would you like to make another query? (Y/N): ")