##this is the class that represents are movie table

##9:10
## the . dot is like the base of our project
from . import db

#9:20 it inherits from db.model
class Movie(db.Model):
    ##and will have 3 colmuns in our table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    rating = db.Column(db.Integer)


    ##10:30 starting database

    ##in terminal 10:55 what create_all() does is that it will take
    ##all the models that exist in our file but not the datbase and create it into the db itself.
    ##and since the database doesnt exist it will create the database for us as well