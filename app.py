from flask import Flask, Response, request
from flask_cors import CORS
import logging
import middleware.context as context
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

def updateRecommendation(recommendation):

    userID = recommendation["userID"]
    movieID = recommendation["movieID"]

    # url for getting recommendation
    url = context.get_recommendation_service_url() + "/recommendations/" + str(userID) + "/" + str(movieID)
    recommendationCheck = requests.get(url)

    if recommendationCheck.status_code == 404:
        # if this recommendation has not been made, insert it
        postUrl = context.get_recommendation_service_url() + "/recommendations/" + str(userID)

        # default values for recommendation
        recommendation["count"] = 1
        recommendation["skipCount"] = 0
        recommendation["swipedYes"] = 0
        response = requests.post(postUrl, json=recommendation)
        if response.status_code != 201:
            logger.error("Error with /recommendations POST: ", response.text)
    else:
        # otherwise, increment the count of the recommendation and use put to update recommendation
        recommendation = recommendationCheck.json()["data"][0]
        recommendation["count"] += 1
        putUrl = context.get_recommendation_service_url() + "/recommendations/" + str(userID) + "/" + str(movieID)
        response = requests.put(putUrl, json=recommendation)
        if response.status_code != 200:
            logger.error("Error with /recommendations/userID/movieID PUT: ", response.text)


##################################################################################################################

@app.route('/')
def hello_world():
    return '<u>Hello World! Welcome to the composition service!</u>'

##### Remove GET later! ######
@app.route('/movieHistorySeqPost', methods=["GET", "POST"])
def userSeqPost():
    return "This will do the sequential post"

##### Remove GET later! ######
@app.route('/movieHistoryParallelPost', methods=["POST"])
def userParallelPost():

    # trying to post a user movie history, first check if movie exists in DB
    body = request.get_json()

    # # # TODO: Check input and assert userID and movieID are present, otherwise cannot post
    # movieID = body["movieID"]
    # movieQuery = "movieID=" + movieID
    # movieUrl = context.get_movie_service_url() + "/movies?movie_id=" + movieID
    # movieCheck = requests.get(movieUrl).json()
    # # if len(movieCheck) == 0:
    # #     # raise error, movie does not exist
    #
    # # if we get here, movie exists, generate its recommendations
    # getRecUrl = context.get_recommendation_service_url() + "/similarity?" + movieQuery
    # postRecUrl = context.get_recommendation_service_url() + "/recommendations"
    # recommendations = requests.get(getRecUrl).json()
    # recommendations = recommendations["recommendations"]
    #
    # # for each recommendation, in parallel, either insert record or increment count
    #
    #
    # rec = recommendations[0]
    # print(recommendations)

    rec = {"userID": body["userID"],
           "movieID": body["movieID"]}
    updateRecommendation(rec)

    return "This will do the parallel post"

# These three are just temporary: to be deleted later
@app.route('/userUrl')
def getUserUrl():
    return str(context.get_user_service_url())

@app.route('/movieUrl')
def getMovieUrl():
    return str(context.get_movie_service_url())

@app.route('/recUrl')
def getRecUrl():
    return str(context.get_recommendation_service_url())

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
