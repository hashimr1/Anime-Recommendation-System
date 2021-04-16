"""CSC111 Final Project: My Anime Recommendations
==========================================================
main.py
==========================================================
@authors: Tu Pham, Tahseen Rana, Raazia Hashim, Meet Patel.
"""
# Imports for evaluating recommendation techniques.
from distance_measures import *
from recommender_evaluation import get_recommender_evaluations

from application import Application
from recommendation_engine import RecommendationEngine
from graph_visualization import present_evaluation_chart


def present_evaluation_data(engine: RecommendationEngine) -> None:
    """Present the graph and the data related to the efficiency of different
    recommendation techniques on web browser."""
    #####################################################################################
    # The actual code to obtain the evaluation data of different recommendation methods.#
    # Not recommended since it may take about 8 minutes.                                #
    #####################################################################################
    # measures = [euclidean_distance, manhattan_distance, minkowski_distance,
    #             jaccard_distance, 'custom', 'graph-based jaccard distance']
    # eval_data = get_recommender_evaluations(measures, engine)
    # accuracies = [(datum[0], datum[1]) for datum in eval_data]
    # running_times = [(datum[0], datum[2]) for datum in eval_data]

    accuracies = [('euclidean_distance', 97), ('manhattan_distance', 97),
                  ('minkowski_distance', 97), ('jaccard_distance', 243), ('custom', 143),
                  ('graph-based jaccard distance', 245), ('content-filtering by genre', 73),
                  ('always return most popular animes', 214)]
    running_times = [('euclidean_distance', 109.1411967), ('manhattan_distance', 111.5982133),
                     ('minkowski_distance', 242.494143), ('jaccard_distance', 82.0985478),
                     ('custom', 5.879013700000087),
                     ('graph-based jaccard distance', 8.566181200000074),
                     ('content-filtering by genre', 5.600600399999962),
                     ('always return most popular animes', 1.2133598000000347)]

    present_evaluation_chart(accuracies, 'accuracy')
    present_evaluation_chart(running_times, 'running time')


if __name__ == '__main__':
    app = Application('Data/animes.csv', 'Data/profiles.csv', 'Data/reviews.csv')

    # For presenting the graph and the bar charts associated with recommender efficiency.
    # This code may take 2 minutes and it is not needed to run the app.
    # recommender = app.recommender
    # recommender.visualize_graph(5000)
    # present_evaluation_data(recommender)

    app.run()
