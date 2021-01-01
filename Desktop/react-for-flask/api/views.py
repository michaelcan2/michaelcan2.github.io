from flask import Blueprint, jsonify, request
##calling the blueprint object main
###since we dont have a different part of the app we will just name oit name
from . import db
from .models import Movie


main = Blueprint('main' , __name__)

##first route
##adding movies is a post request
@main.route('/add_movie', methods=['POST'])
##adding to the databse
def add_movie():
    ###so what this endpoint should be expecting is json data #12:30
    ##this json data is going to be very simple its going to have a movie title and a movie rating.
    ###and with that we should have enough info to save it to the database
####so the first thing we want to do it to GET the data so we use the request library.
    ##giving a varable name to the json we recieve from the db
    movie_data = request.get_json()
##Then we create another movie object using are class Movie from models.py so we can add that to the db.
##so we need to from . import db from .models import Movie ##so just .<name of somthing> refers to another file within are project
##just dot refers to the __init__.py
    ##so with the Movie class we can create another movie object
    ##and the new movie being made needs just two things, the title and the rating
        ##the title comes from movie_data which is a json object aka dictionary and the name of the key that we want is
    ##title, and then will have the rating as well (prob use the class to write out the name and our rating)
    new_movie = Movie(title=movie_data['title'], rating=movie_data['rating'])


    ##so now that we have this new movie we can add it to the commit

    db.session.add(new_movie)
    db.session.commit()


##so all we did was taking the data from the request adding it to the database and comitting
    return 'its been added to the database michael!!', 201
##this other endpoint will display all the movies
##this is the second endpoint
##this should return the movies along with their ratings
##and to do that we need to query the movie table
@main.route('/movies')
def movies():

##this should return the movies along with their ratings
##and to do that we need to query the movie table
##aND to do that we will create a class and sql alchemy allows us to query directly on the class
##which this line below is just saying that we want all the movies that exist
    ##now we need to go through this movies_list and put the data the movies array.
##we cant send movies_list directly to jsonify b/c this is a sql alchemy query result object so it doesnt
##work as json data it needs to be either a list or a dictionary.


    movies_list = Movie.query.all()

#we will get the list of movies from the database but for right now we will start with an empty array.
    movies = []

##so what were going to do is inside trhis list we will append to it.
    for movie in movies_list:
        movies.append({"title": movie.title, "rating": movie.rating})

    ##will return this array through a JSON object
##to do this we need to import jsonify to convert our array to json data
###***WHICH will appear as an array to REACT once it receives it
                    ##'movies in quptesis the key and the value is the the array
                    ##its a dict aka a json
    return jsonify({'movies': movies })
