import googlemaps
from datetime import datetime
gmaps = googlemaps.Client(key='AIzaSyAESaJKQx3j5V27M4FelaWsptwGhn9tkQg')
 
 
dict =  gmaps.places_nearby((37.408690, -122.074761),
                     language='en-AU', min_price=1,
                     max_price=4, keyword='restaurant',
                     rank_by='distance')
                     
for key in dict['results']:
     latitude = key['geometry']['location']['lat']
     longitude = key['geometry']['location']['lng']
     
     print key['name'] + "has a rating of " + str(key['rating']) + "at at location of " + str(latitude) + ", " + str(longitude)
     
 
     
print "Weifu Sucks at basketball"
 
directions_result = gmaps.directions("Sydney", "Melbourne",
                                       mode="bicycling",
                                       avoid=["highways", "tolls", "ferries"],
                                       units="metric",
                                       region="us")
 
print directions_result