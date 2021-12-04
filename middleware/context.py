
import os

def get_user_service_url():

    return os.environ.get("COMP_USER_HOST", None)

def get_movie_service_url():

    return os.environ.get("COMP_MOVIE_HOST", None)

def get_recommendation_service_url():

    return os.environ.get("COMP_REC_HOST", None)
