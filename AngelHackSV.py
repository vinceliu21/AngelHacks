import requests
import googlemaps
import operator
from datetime import datetime
#import Ipython

def main():
    #RETURN_DIRECTIONS()
    retrieveAllConcepts("I want medicine and would like to visit a library")
    # test = ["medicine", "books", "gym"]
    # retrieveRelatedKeywords(test)

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
    concept_list_formatted_trimmed = set(concept_list_formatted) #Remove redundancies
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
def retrieveGooglePlacesData(final_keywords):
    gmaps = googlemaps.Client(key='AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg')
    final_dict = dict()
    for category in final_keywords:
        final_dict[category] = dict()
        query_map =  gmaps.places_nearby((37.408690, -122.074761), language='en-AU', keyword=category, radius=2000)


        for related_place in query_map['results']:
            # ipython.embed()
            related_name = related_place['name']
            final_dict[category][related_name] = dict()
            latitude = related_place['geometry']['location']['lat']
            longitude = related_place['geometry']['location']['lng'] 
            final_dict[category][related_name]['latitude'] = latitude
            final_dict[category][related_name]['longitude'] = longitude
            #final_dict[category][related_name]['place_id'] = 
   
            if related_place.has_key('rating'):
                final_dict[category][related_name]['rating'] = related_place['rating']

            place_reference = related_place['reference']
            url = "https://maps.googleapis.com/maps/api/place/details/json?reference="
            place_request = requests.get(url + place_reference + "&key=AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg" )
            dict_places = place_request.json()["result"]
            place_results= place_request.json()["result"]
            final_dict[category][related_name]['place_id'] = place_results['place_id']
            count = 0
            aggregate_score = 0
            if place_results.has_key("reviews"):

                for individual_review in place_results["reviews"]:
                    review_test = individual_review["text"]
                    count = count + 1
                    if review_test != "":
                        score = retrieveSentiment(review_test)
                        aggregate_score = aggregate_score + score
            if count != 0:
                final_dict[category][related_name]['num_reviews'] = count
                final_dict[category][related_name]['average_sentiment'] = aggregate_score / count
            else:
                final_dict[category][related_name]['num_reviews'] = 0
                final_dict[category][related_name]['average_sentiment'] = 0
    search(final_dict)
            

"""
Takes a string literal
Uses HPE Haven Demand's Sentiment Analysis API
Returns an overall sentiment score
"""

def search(final_dict):
    final_path = []
    #best_score = 0
    poop = ""

    place_to_go = ""

    path_places = []

    for category in final_dict:
        best_score = 0
        for place in final_dict[category]:
            #print final_dict[category][place]['place_id']
            if final_dict[category][place]['average_sentiment'] > best_score:
                best_score = final_dict[category][place]['average_sentiment']
                place_to_go = final_dict[category][place]['place_id']
                poop = place

        path_places.append(place_to_go)
        final_path.append(poop)

    RETURN_DIRECTIONS(path_places)

def RETURN_DIRECTIONS(path_places):
    gmaps = googlemaps.Client(key='AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg')
    #routes = gmaps.directions(path_places[0], path_places[1])

    #https://maps.googleapis.com/maps/api/directions/json?origin=Toronto&destination=Montreal&key=YOUR_API_KEY

    #url = "https://maps.googleapis.com/maps/api/place/details/json?reference="
    #place_request = requests.get(url + place_reference + "&key=AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg" )
    place_request = requests.get("https://maps.googleapis.com/maps/api/directions/json?origin=place_id:" + path_places[1] + "&destination=place_id:" + "&key=AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg")

    ok = place_request.json()

    print ok
    #Ipython.embed()
    #for i in ok['routes'][0]['legs']:
        #print "hi"
        #print i['steps']['html_instructions']
        #print i['html_instructions']
        #print i['duration']['text']
        #print ok['routes']['legs']['duration']['value']

    #for i in ok['routes'][0]['legs'][0]['steps']:
     #   print i['html_instructions']
    #print ok['routes'][0]['legs'][0]['steps'][0]['html_instructions']
    #directions = ok['routes'][0][]

   # print ok['routes'][0]['legs']
    #print place_request['status']









def retrieveSentiment(place_review):
    hpeURLPart1 = "https://api.havenondemand.com/1/api/sync/analyzesentiment/v1?text=" 
    hpeURLPart2 = "&apikey=7cbdd4a6-b09c-4eac-809e-fcb2dd941819"
    place_review_new = place_review.replace(" ", "+")
    res = requests.get(hpeURLPart1 + place_review_new + hpeURLPart2)
    overall_sentiment_score = res.json()["aggregate"]["score"]
    return overall_sentiment_score

main()


