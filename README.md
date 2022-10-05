# Overview
The RPG Stack Exchange website offers a place for game masters and players of tabletop role-playing games to ask and answer questions. It is a great 
resource for those that enjoy tabletop RPGs and the website supports questions about many different RPG systems such as Dungeons \& Dragons, World of Darkness, 
Pathfinder and Apocalypse World. We decided to use this website for our search system because we are both familiar with the many aspects of tabletop gaming 
and it’s generally a topic we enjoy reading about. The RPG world is filled with many different types of players, from players that enjoy more roleplay-based 
games, to players that focus on minimizing and maximizing their character’s skills and attributes. Regardless of playstyle, the RPG Stack Exchange offers 
many interesting and engaging discussions for all types of players to read and enjoy.

For this project, we developed two search systems for the RPG Stack Exchange website.

# Usage
The large file consisting of the posts of the RPG Stack Exchange website is not included. You have to manually download it and drop the Posts.xml file into the /data folder. Once you have done this, most files should be able to run. Some require generation from other files, such as Project1_WordCloud.ipynb and Project1_WordCount.py. The primary search system files are:
* Project1_BooleanSearchSystem.py
* Project1_InvertedIndexSearchSystem.py

These two can be run independently as long as the Posts.xml file exists in /data. 

# Boolean Search System Usage
The Boolean Search System is run by the Project1_BooleanSearchSystem.py file. 

The system will first ask user whether it is their time parsing the posts. 

* If yes, the system will go through all the posts to generate an inverted index where it is saved as {term: {document, document, document}}. Once done processing, the system will save the results in a TSV file for easier usage later.
* If no, the system will look for the TSV file previously generated and created the inverted index from the file. 

After, the user will be asked to input a boolean query. A boolean query has the following potential formats:
* spells AND resurrection
or
* attributes OR skills OR abilities

The system will parse this query into separate words, searching the vocabulary one by one. To begin, the documents associated with the first word are pulled. Next, the search system saves the boolean operator given. Then, we get the documents for the second query word and apply the boolean operator to our gathered documents. In the case of the AND operator, the system will take word1’s documents and word2’s documents and get the documents in which both words appear, so the intersection of the documents. In the case of the OR operator, the system will take word1’s documents and word2’s documents and combine them into one set, as the user wants documents in which either appears. 

This process is repeated until all of the query words and boolean operators are processed. Once finished, the system will print out the top 50 documents for the given query. If there are not 50 documents, it reports as many as it could find. The system then asks if the user would like to make another query.

# Inverted Index Search System Usage
The Inverted Index Search System is run by the Project1_InvertedIndexSearchSystem.py file. 

The system will first ask user whether it is their time parsing the posts. 

* If yes, the system will go through all the posts to generate an inverted index where it is saved as {term: {document: count, document: count, document: count}}. Once done processing, the system will save the results in a TSV file for easier usage later.
* If no, the system will look for the TSV file previously generated and created the inverted index from the file. 

After, the user will be asked to input a query. A query can be anything long or short. However, it does not consider stopwords because stopwords are removed from the vocabulary. Using the given query, the system parses it into individual words and finds the documents associated with each word. The system will then combine the frequencies of terms with matching documents to get the score of that document. For example, consider the query “spell casting”. The system pulls the following for “spell”: spell: {5291: 8, 423: 4, 1992: 1}. Then, the system pulls the following for “casting”: casting: {9129: 12, 423: 5, 1992: 1}. The search system combines the two dictionaries based on documents, so the union becomes {9129: 12, 423: 9, 5291: 8, 1992: 2}. However, the system only wants documents in which both words appear, so any documents in one set but not the other are removed. Our final results for the query “spell casting” would be {423: 9, 1992: 2}.

Once a query has been processed, the system will print out the top-50 documents. This search system ranks documents based on its frequencies. Once results have been printed, the system then asks if the user would like to make another query.
