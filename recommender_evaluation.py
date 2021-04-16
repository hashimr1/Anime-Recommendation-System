"""CSC111 Final Project: My Anime Recommendations
===============================================================
The recommender_evaluation module.

This module contains methods to evaluate the efficiency of our
recommendation engine.
================================================================
@author: Tu Pham
"""
import csv
from typing import Callable, Union
from timeit import default_timer as timer
from recommendation_engine import RecommendationEngine
from anime_graph import User


def get_collab_guess_nums(recommender: RecommendationEngine, test_file: str,
                          distant_measure: Union[Callable[[User, User], float], str]) \
        -> tuple[int, float]:
    """This function runs through the test file. For each user, it tries to provide a list of
    recommendations, based on the collaborative approach, twice the length of the user's list
    of liked anime in the test file.
    Then, it look for how many recommendations match the animes in the list in test file.

    It returns a list of tuples. Each tuple contains the number of correct guesses and the
    running time.

    Preconditions:
        - The test_file is the file extracted from profiles.csv, containing usernames and the
        corresponding extracted anime liked list.
    """
    correct_count = 0
    start = timer()
    with open(test_file) as fp_in:
        reader = csv.reader(fp_in)

        for row in reader:
            liked_list = [int(uid) for uid in row[3][2:-2].split('\', \'')]
            num_liked = len(liked_list)
            recommendations = [anime.uid
                               for anime in recommender.recommend_by_users(row[0], num_liked * 2,
                                                                           distant_measure)]
            for uid in liked_list:
                if uid in recommendations:
                    correct_count += 1
    end = timer()
    running_time = end - start

    return (correct_count, running_time)


def get_content_guess_nums(recommender: RecommendationEngine, test_file: str) -> tuple[int, float]:
    """This function runs through the test file. For each user, it tries to provide a list of
    recommendations, based on the content-filtering approach, twice the length of the user's
    list of liked anime in the test file.
    Then, it look for how many recommendations match the animes in the list in test file.

    It returns a list of tuples. Each tuple contains the number of correct guesses and the
    running time.

    Preconditions:
        - The test_file is the file extracted from profiles.csv, containing usernames and the
        corresponding extracted anime liked list.
    """
    start = timer()
    correct_count = 0
    with open(test_file) as fp_in:
        reader = csv.reader(fp_in)

        for row in reader:
            liked_list = [int(uid) for uid in row[3][2:-2].split('\', \'')]
            num_liked = len(liked_list)
            recommendations = [anime.uid
                               for anime in recommender.recommend_by_genres(row[0], num_liked * 2)]
            for uid in liked_list:
                if uid in recommendations:
                    correct_count += 1

    end = timer()
    running_time = end - start
    return (correct_count, running_time)


def get_prediction_guess_nums(recommender: RecommendationEngine, test_file: str) \
        -> tuple[int, float]:
    """This function runs through the test file. For each user, it tries to provide a list of
    recommendations, based on predictions of review score, twice the length of the user's
    list of liked anime in the test file.
    Then, it look for how many recommendations match the animes in the list in test file.

    It returns a list of tuples. Each tuple contains the number of correct guesses and the
    running time.

    Preconditions:
        - The test_file is the file extracted from profiles.csv, containing usernames and the
        corresponding extracted anime liked list.
    """
    correct_count = 0
    start = timer()
    with open(test_file) as fp_in:
        reader = csv.reader(fp_in)

        for row in reader:
            liked_list = [int(uid) for uid in row[3][2:-2].split('\', \'')]
            num_liked = len(liked_list)
            recommendations = [anime.uid
                               for anime in
                               recommender.recommend_by_score_prediction(row[0], num_liked * 2)]
            for uid in liked_list:
                if uid in recommendations:
                    correct_count += 1
    end = timer()
    running_time = end - start
    return (correct_count, running_time)


def get_popular_guess_nums(recommender: RecommendationEngine, test_file: str) -> tuple[int, float]:
    """This function runs through the test file. For each user, it tries to provide a list of
    recommendations, based on predictions of review score, twice the length of the user's
    list of liked anime in the test file.
    Then, it look for how many recommendations match the animes in the list in test file.

    It returns a list of tuples. Each tuple contains the number of correct guesses and the
    running time.

    Preconditions:
        - The test_file is the file extracted from profiles.csv, containing usernames and the
        corresponding extracted anime liked list.
    """
    correct_count = 0
    start = timer()
    with open(test_file) as fp_in:
        reader = csv.reader(fp_in)

        for row in reader:
            liked_list = [int(uid) for uid in row[3][2:-2].split('\', \'')]
            num_liked = len(liked_list)
            recommendations = [anime.uid
                               for anime in
                               recommender.fetch_popular_anime(num_liked * 2)]
            for uid in liked_list:
                if uid in recommendations:
                    correct_count += 1

    end = timer()
    running_time = end - start
    return (correct_count, running_time)


def get_recommender_evaluations(measures: list[Union[str, Callable]],
                                recommender: RecommendationEngine) -> list[tuple[str, int, float]]:
    """Return a list of tuples, corresponding to the name of user proximity measures, the number
    of correct guesses made, and the running time."""

    res_so_far = []
    for func in measures:
        func_name = func if isinstance(func, str) else func.__name__
        count, running_time = get_collab_guess_nums(recommender,
                                                    'Data/profiles_extracted.csv',
                                                    func)
        res_so_far.append((func_name, count, running_time))

    count, running_time = get_content_guess_nums(recommender,
                                                 'Data/profiles_extracted.csv')
    res_so_far.append(('content-filtering by genre', count, running_time))
    count, running_time = get_popular_guess_nums(recommender,
                                                 'Data/profiles_extracted.csv')
    res_so_far.append(('always return most popular animes', count, running_time))

    return res_so_far
