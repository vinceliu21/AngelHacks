import requests
# import nltk
# from nltk.corpus import wordnet as wn
import googlemaps
from datetime import datetime

"""
Takes a string literal!
Uses HPE Haven Demand's Concept Extraction API
Retrieves a list of pertinent concepts
Filters out only nouns
Does additional filtering & processing
Returns a list of final keywords
"""
def retrieveAllConcepts(alexa_output):  
    hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/extractconcepts/v1?text=" 
    hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
    alexa_output_decomposed = alexa_output.split(" ")
    alexa_output_new = ""
    for alexa_output_component in alexa_output_decomposed:
        alexa_output_new += alexa_output_component + " + "
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

            if key.has_key("rating"):
                print key['name'] + " has a rating of " + str(key['rating']) + " at a location of " + str(latitude) + ", " + str(longitude)
            else:
                print key['name'] + " at a location of " + str(latitude) + ", " + str(longitude)

retrieveAllConcepts("I want medicine and would like to visit a library")

