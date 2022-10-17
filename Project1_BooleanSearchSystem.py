# Imports
from codecs import utf_8_encode
import nltk
import time
from nltk.corpus import stopwords
from nltk.corpus.reader.tagged import word_tokenize
import re, string
import csv
import sys

# Post Reader
from post_parser_record import PostParserRecord
post_reader = PostParserRecord("data/Posts.xml")            # Interchangeable with line 5
#post_reader = PostParserRecord("data/Posts_Small.xml")     # Interchangeable with line 4
stop_words = stopwords.words('english')

""" CODE FROM USER user1251007 ON STACKOVERFLOW START """
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
""" CODE FROM USER user1251007 ON STACKOVERFLOW END """

def createBooleanIndex():
    """
    This function counts all of the words in both the questions
    and answers. Keeps track of word count in word_dict.
    """
    print("Processing questions...")

    # For each question
    for answer_id in post_reader.map_questions:
        # Get text
        text = (post_reader.map_questions[answer_id].title + " " + post_reader.map_questions[answer_id].body)
        # Remove punctuations, Make lowercase
        # Tokenize words into list
        token_words = re.sub("<.*?>|\\n|&quot;", " ", text.lower())
        token_words = word_tokenize(token_words.translate(str.maketrans('', '', string.punctuation)))
        token_words = [word for word in token_words if word not in stop_words]
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
    
    print("Processing answers...")
    # For each answer
    for answer_id in post_reader.map_just_answers:
        # Get text
        text = (post_reader.map_just_answers[answer_id].body)
        # Remove punctuations, Make lowercase
        # Tokenize words into list
        token_words = re.sub("<.*?>|\\n|&quot;", " ", text.lower())
        token_words = word_tokenize(token_words.translate(str.maketrans('', '', string.punctuation)))
        token_words = [word for word in token_words if word not in stop_words]
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
    """
    This function saves word_dict into a TSV file and
    saves it to /data.
    """
    print("Saving data to TSV...")
    keys = ['Word', 'Documents']

    with open("data/InvertedIndex.tsv", "w", encoding="utf-8", newline='') as f:
        dict_writer = csv.DictWriter(f, keys, delimiter='\t')
        dict_writer.writeheader()
        for word in word_dict:
            dict_writer.writerow({"Word": word, "Documents": word_dict[word]})

def processTSV():
    """
    processTSV() will open the TSV file at data/InvertedIndex.tsv
    and parse it into word_dict as {words : {docs}}.
    """
    with open("data/InvertedIndex.tsv", encoding="utf-8") as f:
        tsv_file = csv.reader(f, delimiter="\t")
        next(tsv_file)
        for line in tsv_file:
            word_dict[line[0]] = {int(doc) for doc in (set(line[1].strip('}{').split(', ')))}

def processQueryWord(word):
    """
    This function looks for word in the word_dict
    and applies the appropriate boolean_op to the
    current results. Returns the product of the operation.
    """
    word = word.lower()
    docs = word_dict.get(word)
    # Check if the word exists in the dictionary; default to empty set if not
    if(type(docs) != set):
        docs = set()
    # check what operation to do
    if(boolean_op == -1): # FIRST WORD
        return docs
    elif(boolean_op == 0): # OR
        return results | docs
    elif(boolean_op == 1): # AND
        return results & docs

def printResults(query, results):
    print(f"The top %d results for the query \"%s\" are: " % (len(results), query))
    for result in results:
        print(result)

# START:
word_dict = {}
validInput = False
printTime = False

# Ask user if they want to reprocess posts; alternative is read from TSV
userInput = input("First time indexing the posts? (Y/N): ")
while validInput == False: 
    if(userInput[0].upper() == 'Y'):
        time_start = time.time()
        createBooleanIndex()       # Generates inverted index from Posts.xml
        time_end = time.time()
        if(printTime):
            print(f'Processing posts from Posts.xml took %.2f s' % (time_end - time_start))
        saveInvertedIndex()         # Saves inverted index in TSV form
        validInput = True
    elif(userInput[0].upper() == 'N'):
        time_start = time.time()
        processTSV()                # Creates the inverted index from the TSV
        time_end = time.time()
        if(printTime):
            print(f'Processing posts from TSV took %.2f s' % (time_end - time_start))
        validInput = True
    else:
        print("Invalid input. Input Y or N")
        userInput = input("First time indexing the posts? (Y/N): ")

# At this point, we have inverted index from reading through the file or processing TSV
# Then we need to get our query from the user
hasAnotherQuery = True
while hasAnotherQuery:
    # Ask user for query:
    userInput = input("Input your boolean query: ")
    parsed_query = userInput.split()
    # variables:
    boolean_op = -1         # Used to keep track of OR and AND. 0 = OR, 1 = AND, -1 = No value atm
    is_next_word = True     # When is_next_word = False, we should have a boolean op next
    invalid_query = False   # When = true, we have invalid query; reask for new query
    results = []            # Keeps track of the results we currently have per word
    # Start timer
    time_start = time.time()
    for word in parsed_query:
        # Check if we need a word or an OP
        if(is_next_word):       # we need word
            if(word.upper() != "OR" and word.upper() != "AND"):
                results = processQueryWord(word)
                is_next_word = False
            else: # We have an OP after an OP
                print("Input query should be of format word BOOL_OP word BOOL_OP ...")
                invalid_query = True
                continue
        else:   # We need an OP
            if(word.upper() == "OR"):
                boolean_op = 0
                is_next_word = True
            elif(word.upper() == "AND"):
                boolean_op = 1
                is_next_word = True
            else: # We have a word after a word
                print("Input query should be of format word BOOL_OP word BOOL_OP ...")
                invalid_query = True
                continue
    # Check if we left bc invalid query
    if (invalid_query):
        continue
    
    time_end = time.time()
    # Sort results via doc id and only take first 50
    results = sorted(list(results))[:50]
    # Print results:
    printResults(userInput, results)
    if(printTime):
        print(f'Retrieving the index took %.2f ms' % ((time_end - time_start)*1000))

    # Ask user if they want another query
    userInput = input("Would you like to make another query? (Y/N): ")
    validInput = False
    while validInput == False:
        if(userInput[0].upper() == 'Y'):
            hasAnotherQuery = True
            validInput = True
        elif(userInput[0].upper() == 'N'):
            hasAnotherQuery = False
            validInput = True
        else:
            print("Invalid input. Input Y or N")
            userInput = input("Would you like to make another query? (Y/N): ")