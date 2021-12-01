from flask import Flask, Response, request
from flask_cors import CORS
import logging
import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
CORS(app)

##################################################################################################################

@app.route('/')
def hello_world():
    return '<u>Hello World! Welcome to the composition service!</u>'

##### Remove GET later! ######
@app.route('/userSeqPost', methods=["GET", "POST"])
def userSeqPost():
    return "This will do the sequential post"

##### Remove GET later! ######
@app.route('/userParallelPost', methods=["GET", "POST"])
def userParallelPost():
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
