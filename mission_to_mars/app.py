# import necessary libraries
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


# create instance of Flask app
app = Flask(__name__)


# Use flask_pymongo for mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

# create route that renders index.html template
@app.route("/")
def index():
    mars = mongo.db.planet.find_one()
    return render_template("index.html", mars=mars)

# create route that calls the scrape.html template to initate Data Scrape
@app.route("/scrape-data.html")
def scrapeData():
    scrape_mars.scrape()
    mars = mongo.db.planet.find()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
