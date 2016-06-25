import requests
import googlemaps
import operator
from datetime import datetime

def main():
    # retrieveAllConcepts("I want medicine and would like to visit a library")
    # retrieveSentiment("I love baseball")
    test = ["medicine", "books", "gym"]
    retrieveRelatedKeywords(test)
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
    final_keywords = filterNounConcepts(concept_list_formatted_trimmed)
    retrieveGooglePlacesData(list(final_keywords))

"""Takes a set of concepts
Hard-coded if statements filter concepts based on irrelevant words
"""
def filterNounConcepts(concept_set_trimmed):
    for keyword in list(concept_set_trimmed):
        if (keyword == "want" or keyword == "need" or keyword == "will" or keyword ==
            "later" or keyword == "today" or keyword == "get" or keyword == "buy" or
            keyword == "see" or keyword == "would" or keyword == "like" or keyword ==
            "a" or keyword == "to" or keyword == "and" or keyword == "visit"):
            concept_set_trimmed.remove(keyword)
    return concept_set_trimmed

"""Takes a list of keywords
Returns a list of top 3 "intelligent" related keywords for Google Places API per category
"""
def retrieveRelatedKeywords(final_keywords):
    related_keywords = []
    for keyword in final_keywords:
        pre_sorted_related_keywords = {} #Text : Occurences
        hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/findrelatedconcepts/v1?text=" 
        hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
        res = requests.get(hpeURLPart1 + keyword + hpeURLPart2)
        related_key_word_list = res.json()["entities"]
        for related_instance in related_key_word_list:
            pre_sorted_related_keywords[related_instance["text"]] = related_instance["occurrences"]
        sorted_related_keywords = sorted(pre_sorted_related_keywords.items(), key = operator.itemgetter(1))
        if (len(sorted_related_keywords)) <= 2:
            for related_key in sorted_related_keywords:
                related_keywords.append(str(related_key[0]))
        else:
            last_index = len(sorted_related_keywords)
            for related_key in sorted_related_keywords[last_index-3:last_index]:    
                related_keywords.append(str(related_key[0]))
    print (related_keywords)

"""
Takes a list of keywords
Returns google data for locations that correspond to the keywords
"""
def retrieveGooglePlacesData(keywords):
    gmaps = googlemaps.Client(key='AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg')
    for keyword in keywords:
        dict =  gmaps.places_nearby((37.408690, -122.074761), language='en-AU', keyword=keyword, rank_by='distance')
        for key in dict['results']:
            latitude = key['geometry']['location']['lat']
            longitude = key['geometry']['location']['lng'] 

            place_reference = key['reference']

            url = "https://maps.googleapis.com/maps/api/place/details/json?reference="
            place_request = requests.get(url + place_reference + "&key=AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg" )

            dict_places = place_request.json()["result"]
            place_results= place_request.json()["result"]
            count = 0
            if place_results.has_key("reviews"):
                #count = 0
                for individual_review in place_results["reviews"]:
                    review_test = individual_review["text"]
                    count = count + 1
                    #score = retrieveSentiment(review_test)
                    if review_test != "":
                        print "review has sentiment analysis of " + str(retrieveSentiment(review_test))
            
            print dict_places['name'] + " has " + str(count) + " reviews"

            if key.has_key("rating"): #Not all places have a rating
                print key['name'] + " has a rating of " + str(key['rating']) + " at a location of " + str(latitude) + ", " + str(longitude)
            else:
                print key['name'] + " at a location of " + str(latitude) + ", " + str(longitude)

"""
Takes a string literal
Uses HPE Haven Demand's Sentiment Analysis API
Returns an overall sentiment score
"""
def retrieveSentiment(place_review):
    hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/analyzesentiment/v1?text=" 
    hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
    place_review_new = place_review.replace(" ", "+")
    res = requests.get(hpeURLPart1 + place_review_new + hpeURLPart2)

   # print place_review
    overall_sentiment_score = res.json()["aggregate"]["score"]
    return overall_sentiment_score

main()
