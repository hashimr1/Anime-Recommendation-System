"""CSC111 Final Project: My Anime Recommendations
===============================================================
The recommendation_engine module.

This module contains the definition of the RecommendationEngine
class and its related function implementations.
================================================================
@author: Tu Pham
"""

from __future__ import annotations
import csv
from anime_graph import AnimeGraph
import graph_visualization


class RecommendationEngine:
    """A Recommendation Engine for anime, using the data collected from
    MyAnimeList.

    Instance Attributes:
        - graph: The graph containing anime, users, and genres.
        - gui: The gui instance of the class GUI, for interaction with the app user.
        - anime_id_to_name: A mapping of anime ids to their name for name look up.
    """
    _graph: AnimeGraph
    # gui: GUI
    _anime_id_to_name: dict[int, str]

    def __init__(self, anime_filepath: str,
                 user_profile_filepath: str, review_filepath: str) -> None:
        """Initializing the Engine."""
        self._anime_id_to_name = {}
        self._graph = AnimeGraph()
        self._load_anime_data(anime_filepath)
        self._load_user_data(user_profile_filepath)
        self._load_review_data(review_filepath)

    def _load_anime_data(self, filepath: str) -> None:
        """Loads the anime data from a file into the graph.
        This will also insert new genres into the graph.
        """
        with open(filepath, 'r', encoding="utf8") as file:
            reader = csv.reader(file)

            # Skip the header
            next(reader)

            for row in reader:
                _convert_anime_row_data_types(row)
                # The data types of elements in row got converted to the correct type already.
                self._graph.add_anime(uid=row[0], title=row[1], synopsis=row[2],
                                      total_episodes=row[5], popularity=row[7],
                                      rank=row[8], score=row[9])
                genres = row[3][2:-2].split('\', \'')
                for genre in genres:
                    if genre != '':
                        self._graph.add_anime_genre_edge(int(row[0]), genre)

    def _load_user_data(self, filepath: str) -> None:
        """Loads the user data from a file into the graph.
        This will also insert new default review scores (weighted edges) for the user's
        favorite anime.

        Preconditions:
            - The file has the format as described in the report.
        """
        with open(filepath, 'r', encoding="utf8") as file:
            reader = csv.reader(file)

            # Skip the header
            next(reader)

            for row in reader:
                _convert_user_row_data_types(row)
                # The types of elements in row got converted appropriately already.
                self._graph.add_user(row[0], row[1], row[2])
                for fav_uid in row[3]:  # row 3 contains a list of favorite anime uid.
                    # giving a default score of 9 to a favorite anime
                    self._graph.add_review(row[0], fav_uid, 9)

    def _load_review_data(self, filepath: str) -> None:
        """Loads the review data from a file into the graph.
        The reviews will be represented by weighted edges between user and anime

        Preconditions:
            - The file has the format as described in the report.
        """
        with open(filepath, 'r', encoding="utf8") as file:
            reader = csv.reader(file)

            # Skip the header
            next(reader)

            for row in reader:
                self._graph.add_review(row[1], int(row[2]), float(row[3]))

    def visualize_graph(self, max_vertices: int = 10000) -> None:
        """Visualize the graph using networkx and plotly.
        Preconditions:
            - The graph has been loaded with the given data.
        """
        graph_visualization.visualize_graph(self._graph, max_vertices=max_vertices)


def _convert_anime_row_data_types(row: list) -> None:
    """Convert a row in the csv reader to the usable format by mutating this row.
    This means:
        - row[0] is an int
        - row[1] is a str
        - row[2] is a str
        - row[5] is int
        - row[7] is either None or int
        - row[8] is either None or int
        - row[9] is either None or float
    """
    row[0] = int(row[0])
    if row[5] == '':
        row[5] = 0
    else:
        row[5] = int(float(row[5]))
    if row[7] == '':
        row[7] = None
    else:
        row[7] = int(row[7])
    if row[8] == '':
        row[8] = None
    else:
        row[8] = int(float(row[8]))
    if row[9] == '':
        row[9] = None
    else:
        row[9] = int(float(row[9]))


def _convert_user_row_data_types(row: list) -> None:
    """Convert a row of user data in the csv reader to the usable format by mutating this row.
    This means:
        - row[0] is a str (the username)
        - row[1] becomes a str or None (The gender of the user)
        - row[2] becomes a int or None (The birth year of the user)
        - row[3] is a list of str (favorite animes) or an empty List
    """
    if row[1] == '':
        row[1] = None

    year = row[2][-4:]
    if year.isnumeric():
        row[2] = int(year)
    else:
        row[2] = None
    fav_list = row[3][2:-2].split('\', \'')
    if fav_list == ['']:
        row[3] = []
    else:
        row[3] = [int(uid) for uid in fav_list]


if __name__ == '__main__':
    engine = RecommendationEngine("Data/animes.csv", 'Data/profiles.csv', 'Data/reviews.csv')
    engine.visualize_graph(1000)
