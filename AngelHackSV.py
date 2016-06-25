import requests
# import nltk
# from nltk.corpus import wordnet as wn
import googlemaps
from datetime import datetime

def main():
    retrieveAllConcepts("I want medicine and would like to visit a library")
    retrieveSentiment("I love baseball")

"""
Takes a string literal
Uses HPE Haven Demand's Concept Extraction API
Retrieves a list of pertinent concepts
Filters out only nouns
Does additional filtering & processing
Returns a list of final keywords
"""
def retrieveAllConcepts(alexa_output):  
    hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/extractconcepts/v1?text=" 
    hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
    alexa_output_new = alexa_output.replace(" ", "+")
    res = requests.get(hpeURLPart1 + alexa_output_new + hpeURLPart2)
    concept_list = res.json()["concepts"]
    concept_list_formatted = []   
    for concept in concept_list:
        if (" " in concept["concept"]): #Concept has multiple words
            concept_decomposed = concept["concept"].split(" ")
            for concept_component in concept_decomposed:
                concept_list_formatted.append(concept_component)
        else:
            concept_list_formatted.append(concept)
    concept_list_formatted_trimmed = set(concept_list_formatted)
    # for concept in concept_list_formatted:
    #     print (str(concept))
    #     if (wn.synsets(concept)[0].pos() == unicode("n", "utf-8")): #If the unicode is a noun
    #         concept_list_nouns.add(str(concept))
    #         print (concept)
    # print (concept_list_nouns)
    final_keywords = filterNounConcepts(concept_list_formatted_trimmed)
    retrieveGooglePlacesData(list(final_keywords))

def filterNounConcepts(concept_set_trimmed):
    for keyword in list(concept_set_trimmed):
        if (keyword == "want" or keyword == "need" or keyword == "will" or keyword ==
            "later" or keyword == "today" or keyword == "get" or keyword == "buy" or
            keyword == "see" or keyword == "would" or keyword == "like" or keyword ==
            "a" or keyword == "to" or keyword == "and" or keyword == "visit"):
            concept_set_trimmed.remove(keyword)
    return concept_set_trimmed

"""
Takes a list of keywords
Returns google data for locations that correspond to the keywords
"""
def retrieveGooglePlacesData(final_keywords):
    gmaps = googlemaps.Client(key='AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg')
    for keyword in final_keywords:
        dict =  gmaps.places_nearby((37.408690, -122.074761), language='en-AU', keyword=keyword, rank_by='distance')

        for key in dict['results']:
            latitude = key['geometry']['location']['lat']
            longitude = key['geometry']['location']['lng'] 

            if key.has_key("rating"): #Not all places have a rating
                print key['name'] + " has a rating of " + str(key['rating']) + " at a location of " + str(latitude) + ", " + str(longitude)
            else:
                print key['name'] + " at a location of " + str(latitude) + ", " + str(longitude)

"""
Takes a string literal
Uses HPE Haven Demand's Sentiment Analysis API
Returns an overall sentiment
"""

def retrieveSentiment(place_review):
    hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/analyzesentiment/v1?text=" 
    hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
    place_review_new = place_review.replace(" ", "+")
    res = requests.get(hpeURLPart1 + place_review_new + hpeURLPart2)
    overall_sentiment_score = res.json()["aggregate"]["score"]
    print (overall_sentiment_score)

main()
