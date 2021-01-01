from flask import Flask
from flask_sqlalchemy import SQLAlchemy



### 8:30 insingle file flask apps (WHICH IS NOT THIS)
##you would normmally  pass in the app when you instanuate the DB for the first time but
##when you use this pattewrn of create app you cant do that
###so you have to instaniate the single alchemy object without the app
####and then inside it you create an aoo function thats where you instaniate the app
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
###for the config we will be using a sqllite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    ##calling the db here
    db.init_app(app)


    ##!! we have to import the .views here so it will work cause it needs to be imported AFTER flask has been not
    ##alll at once
    ##"main" being the name of the entire file called views
    from .views import main
    ##. register will register the blueprint
    app.register_blueprint(main)

    ####later will use the db object that we create later to instantiate the app with this database but
    ##for now will return app
    return app

##there will be two endpoints in this app one to view the movies, and another to add the movies

