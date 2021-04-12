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
from typing import Optional
from anime_graph import AnimeGraph, Anime, Genre, User
import graph_visualization

# The lowest score that indicate a favorite anime.
SCORE_FAVORITE = 8


class RecommendationEngine:
    """A Recommendation Engine for anime, using the data collected from
    MyAnimeList.

    Instance Attributes:
        - graph: The graph containing anime, users, and genres.
        - gui: The gui instance of the class GUI, for interaction with the app user.
        - anime_id_to_name: A mapping of anime ids to their name for name look up.
    """
    _graph: AnimeGraph
    # _gui: GUI
    current_user: Optional[User]

    def __init__(self, anime_filepath: str,
                 user_profile_filepath: str, review_filepath: str) -> None:
        """Initializing the Engine."""
        self._graph = AnimeGraph()
        self._load_anime_data(anime_filepath)
        self._load_user_data(user_profile_filepath)
        self._load_review_data(review_filepath)
        self.current_user = None

    def log_in(self, username) -> bool:
        """Log a user into the system.
        Returns whether the log in is successful. It is unsuccessful when there is already
        an user logged in, or there is no user with the matching username.
        """
        if self.current_user is None and username in self._graph.users:
            self.current_user = self._graph.users[username]
            return True
        else:
            return False

    def log_out(self) -> bool:
        """Log out for the user currently logging in.
        Returns whether the log out attempt is successful. When there is no user currently
        logged in, it returns False.
        """
        if self.current_user is not None:
            self.current_user = None
            return True
        else:
            return False

    def recommend(self, limit: int = 10) -> list[Anime]:
        """Returns a list of anime for the currently logged in user, as suggestions.
        Returns an empty list if the user has not reviewed any anime.
        Function Parameters:
            - limit: the maximum number of allowed
        Preconditions:
            - self.current_user is not None
        """
        exclusions = set(self.current_user.neighbor_anime.keys())
        if len(self.current_user.neighbor_anime) == 0:
            return []
        elif len(self.current_user.neighbor_anime) < 3:
            # Get the 5 most liked genres for content filtering
            liked_genres = self.current_user.best_liked_genres(5)
            return self._recommend_by_genres(liked_genres, limit, exclusions)
        else:
            # By default, get 50 most similar users.
            similar_users = self.current_user.most_similar_users()
            return self._recommend_by_users(similar_users, limit, exclusions)

    def _recommend_by_genres(self, genres: list[tuple[Genre, float]], limit: int = 10,
                             exclusions: set[Anime] = None) -> list[Anime]:
        """Returns a list of most matched anime in term of genres, up to a limit, sorted by match
        score and popularity, excluding the anime in the set exclusions."""
        matched_so_far = {}
        num_ani = len(self._graph.anime)
        for tup in genres:
            for anime in tup[0].neighbor_anime:
                if anime not in exclusions and anime.popularity is not None:
                    if anime in matched_so_far:
                        matched_so_far[anime] += (num_ani - anime.popularity) * tup[1]
                    else:
                        matched_so_far[anime] = (num_ani - anime.popularity) * tup[1]
        result_list = [(ani, matched_so_far[ani]) for ani in matched_so_far]
        result_list.sort(key=lambda x: x[1], reverse=True)
        if len(result_list) <= limit:
            return [ele[0] for ele in result_list]
        else:
            return [ele[0] for ele in result_list[:limit]]

    def _recommend_by_users(self, similar_users: list[tuple[User, float]], limit: int = 10,
                            exclusions: set[Anime] = None) -> list[Anime]:
        """Returns a list of anime recommendations, up to a limit, based on similar users.
        """
        recommended_so_far = {}
        for tup in similar_users:
            for anime in tup[0].neighbor_anime:
                rating = tup[0].neighbor_anime[anime]
                if anime not in exclusions and rating >= 8:
                    if anime in recommended_so_far:
                        recommended_so_far[anime] = max(recommended_so_far[anime], rating * tup[1])
                    else:
                        recommended_so_far[anime] = rating * tup[1]
        result_list = [(ani, recommended_so_far[ani]) for ani in recommended_so_far]
        result_list.sort(key=lambda x: x[1], reverse=True)
        if len(result_list) <= limit:
            return [ele[0] for ele in result_list]
        else:
            return [ele[0] for ele in result_list[:limit]]

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
