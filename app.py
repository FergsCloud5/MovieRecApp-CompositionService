import json
from datetime import datetime

import asyncio
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

async def updateRecommendation(recommendation):

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
        return response
    else:
        # otherwise, increment the count of the recommendation and use put to update recommendation
        recommendation = recommendationCheck.json()["data"][0]
        recommendation["count"] += 1
        putUrl = context.get_recommendation_service_url() + "/recommendations/" + str(userID) + "/" + str(movieID)
        response = requests.put(putUrl, json=recommendation)
        if response.status_code != 200:
            logger.error("Error with /recommendations/userID/movieID PUT: ", response.text)
        return response

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
async def userParallelPost():
    try:
        # trying to post a user movie history, first check if movie exists in DB
        body = request.get_json()
        userID = body.get("userID", None)
        movieID = body.get("movieID", None)
        if not userID or not movieID:
            return Response("Must provide userID and movieID", status=400)

        # check if this movie exists in DB
        movieQuery = "movieID=" + movieID
        movieUrl = context.get_movie_service_url() + "/movies?movie_id=" + movieID
        movieCheck = requests.get(movieUrl)
        movieStatus = movieCheck.status_code
        movieCheck = movieCheck.json()
        if len(movieCheck) == 0 or movieStatus != 200:
            return Response("Movie does not exist.", status=404)

        # construct movie history and make insertion into userMovieHistory first
        historyUrl = context.get_user_service_url() + "/movie-histories"
        movieHistory = {"userID": userID,
                        "movieID": movieID,
                        "movieTitle": movieCheck[0]["movie_title"],
                        "likedMovie": body.get("likedMovie", 0)}
        historyPost = requests.post(historyUrl, json=movieHistory)
        if historyPost.status_code != 201:
            return Response(historyPost, content_type="application/json")

        # if we get here, movie exists and was posted, generate its recommendations only if user liked movie
        if movieHistory["likedMovie"] == 1:
            getRecUrl = context.get_recommendation_service_url() + "/similarity?" + movieQuery
            recommendations = requests.get(getRecUrl).json()
            recommendations = recommendations["recommendations"]
            # for each recommendation, in parallel, either insert record or increment count
            rs = (updateRecommendation({"userID": body["userID"], "movieID": recommendation["movieID"]}) for recommendation in recommendations)
            L = await asyncio.gather(*rs)
            print(L)

        # if all succeeds, return regular response for user movie history post, so service works like before
        # return Response(historyPost.json(), status=historyPost.status_code, content_type="application/json")
        return Response(historyPost, content_type="application/json")

    except Exception as e:
        statusRespDict = {
            "status": "500 Internal server error",
            "error message": str(e)
        }
        rsp = Response(json.dumps(statusRespDict), status=500, content_type='application/json')
        return rsp

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
