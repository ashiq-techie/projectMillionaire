from __future__ import division, unicode_literals

import pandas as pd
import re,sys,math
import nltk
from gensim.models import Word2Vec
# nltk.download()
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
import numpy as np  # Make sure that numpy is imported

import cPickle

test = pd.read_csv("../../backupData/crawledProcessedData/check.csv", header=0, delimiter=",", quotechar="\"")
train = pd.read_csv("../../backupData/crawledProcessedData/completeQuoteArticleMappingPart4New.csv", header=0, delimiter=",", quotechar="\"")

train.columns = list(test.columns.values)


# makes the individual avg tfidf vector array

def makeFeatureVec(words, model, num_features, weights, index2word_set):
    # Function to average all of the word vectors in a given
    # paragraph
    #
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((num_features,),dtype="float32")
    #
    nwords = 0.
    # 
    
    #
    # Loop over each word in the review and, if it is in the model's
    # vocaublary, add its feature vector to the total
    for word in words:
        if word in index2word_set: 
            nwords = nwords + 1.
            if word in weights:
                weight = weights[word]
            else:
                weight = 0.0
            weightMultipliedVector = (weight+1)*model[word]
            featureVec = np.add(featureVec,weightMultipliedVector)
    # 
    # Divide the result by the number of words to get the average
    featureVec = np.divide(featureVec,nwords)
    return featureVec


def getAvgFeatureVecs(reviews, model, num_features, weights, index2word_set):
    # Given a set of reviews (each one a list of words), calculate 
    # the average feature vector for each one and return a 2D numpy array 
    # 
    # Initialize a counter
    counter = 0.
    # 
    # Preallocate a 2D numpy array, for speed
    reviewFeatureVecs = np.zeros((len(reviews),num_features),dtype="float32")
    # 
    # Loop through the reviews
    for review in reviews:
        #
        # Print a status message every 1000th review
        if counter%1000. == 0.:
            print "Review %d of %d" % (counter, len(reviews))
        # 
        # Call the function (defined above) that makes average feature vectors
        reviewFeatureVecs[counter] = makeFeatureVec(review, model, num_features, weights, index2word_set)
        #
        # Increment the counter
        counter = counter + 1.
    return reviewFeatureVecs

def getTfidfWeights(corpus):
    tfidf = TfidfVectorizer(min_df=1)
    tfs = tfidf.fit_transform(corpus)

    feature_names = tfidf.get_feature_names()

    weights = {}
    for col in tfs.nonzero()[1]:
        weights[feature_names[col]] = tfs[0, col]
    return weights




print "Cleaning and parsing the training set...\n"
# Get the number of reviews based on the dataframe column size
num_articles = train["body"].size
print num_articles


# Initialize an empty list to hold the clean reviews
clean_train_articles = []

# Loop over each review; create an index i that goes from 0 to the length
# of the movie review list 
for i in xrange( 0, num_articles ):
    # If the index is evenly divisible by 1000, print a message
    if( (i+1)%1000 == 0 ):
        print "Review %d of %d\n" % ( i+1, num_articles )                                                   
    clean_train_articles.append(train["body"][i])



num_test_articles = test["body"].size
# Initialize an empty list to hold the clean reviews

clean_test_articles = []

# Loop over each review; create an index i that goes from 0 to the length
# of the movie review list 
for i in xrange( 0, num_test_articles ):
    # If the index is evenly divisible by 1000, print a message
    if( (i+1)%1000 == 0 ):
        print "Review %d of %d\n" % ( i+1, num_test_articles )                                                   
    clean_test_articles.append(test["body"][i])



# get tfidf

weights = getTfidfWeights(clean_train_articles+clean_test_articles)

# estimate sentiments

print "loading model"


model = Word2Vec.load_word2vec_format('../../backupData/preTrainedModels/models/GoogleNews-vectors-negative300/GoogleNews-vectors-negative300.bin', binary=True)
# Index2word is a list that contains the names of the words in 
# the model's vocabulary. Convert it to a set, for speed 
print "Creating word index set"
index2word_set = set(model.index2word)
print "Processing training set"
trainDataVecs = getAvgFeatureVecs(clean_train_articles, model, 300, weights, index2word_set)
print "Processing Test set"
testDataVecs = getAvgFeatureVecs(clean_test_articles, model, 300, weights, index2word_set)


output = pd.DataFrame( data=trainDataVecs)
output.to_csv( "../../backupData/models/learnedModels/trainDataVecsFromGoogle.csv", index=False )
output = pd.DataFrame( data=testDataVecs)
output.to_csv( "../../backupData/models/learnedModels/testDataVecsFromGoogle.csv", index=False )
