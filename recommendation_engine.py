"""CSC111 Final Project: My Anime Recommendations
===============================================================
The recommendation_engine module.

This module contains the definition of the RecommendationEngine
class and its related function implementations.
================================================================
@author: Tu Pham
"""

from __future__ import annotations
from typing import Optional, Callable, Union
import csv

import graph_visualization
from anime_graph import AnimeGraph, Anime, User
from distance_measures import jaccard_distance

# The lowest score that indicate a favorite anime.
SCORE_FAVORITE = 9


class RecommendationEngine:
    """A Recommendation Engine for anime, using the data collected from
    MyAnimeList.

    Instance Attributes:
        - graph: The graph containing anime, users, and genres.
        - gui: The gui instance of the class GUI, for interaction with the app user.
        - anime_id_to_name: A mapping of anime ids to their name for name look up.
    """
    _graph: AnimeGraph

    def __init__(self, graph: AnimeGraph) -> None:
        """Initializing the Engine."""
        self._graph = graph

    def check_user_exists(self, username: str) -> bool:
        """Returns whether the username is in the system."""
        return username in self._graph.users

    def register(self, username: str, gender: str, date_birth: str, filepath: str) -> bool:
        """Register for a new user. If the user is already in the system, return false.
        If the registering is successful, return true.
        Preconditions:
            - username != ''
            - gender in {'male', 'female', 'other'}
            - date_birth != ''
            - the last 4 characters in date_birth is a year.
        """
        if username in self._graph.users:
            return False
        else:
            new_row = [username, gender, date_birth, []]
            with open(filepath, 'a+', newline='') as fd:
                writer = csv.writer(fd)
                writer.writerow(new_row)
            self._graph.add_user(username, gender, int(date_birth[-4:]))
            return True

    def add_review(self, username: str, anime_uid: int, review_score: float,
                   reviews_filepath: str) -> None:
        """Add a review to the database and the graph.
        Preconditions:
            - username in self._graph
            - anime in self._graph
        """
        # String form of the score
        s = str(review_score)
        # For now we don't use the details of categorized score yet
        pseudo_details = {'Overall': s, 'Story': s, 'Animation': s, 'Sound': s,
                          'Character': s, 'Enjoyment': s}
        # The '0' is a temporary review ID, we don't need it for now.
        new_row = ['0', username, anime_uid, s, pseudo_details]
        with open(reviews_filepath, 'a+', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerow(new_row)
        # This will overwrite the current user-anime edge, if there is any.
        self._graph.add_review(username, anime_uid, review_score)

    def fetch_new_anime(self, limit: int = 10) -> list[Anime]:
        """Returns a list of newly released anime, up to a limit."""
        return self._graph.fetch_new_anime(limit)

    def fetch_anime_by_name(self, name: str) -> Optional[Anime]:
        """Returns an anime in the system.
        If there is none, returns None."""
        return self._graph.fetch_anime_by_name(name)

    def fetch_popular_anime(self, limit: int = 10) -> list[Anime]:
        """Returns a list of most popular anime, up to a limit"""
        return self._graph.fetch_popular_anime(limit)

    def fetch_popular_by_genre(self, genre: str, limit: int = 10) -> list[Anime]:
        """Returns a list of most popular anime of a given genre, up to a limit."""
        return self._graph.fetch_popular_by_genre(genre, limit)

    def fetch_all_genres(self) -> list[str]:
        """Return the list of all anime genres, sorted in alphabetical order."""
        return self._graph.fetch_all_genres()

    def recommend(self, username: str, limit: int = 10) -> list[Anime]:
        """Returns a list of anime for the given user, as suggestions.
        Returns an empty list if the user has not reviewed any anime.
        Function Parameters:
            - limit: the maximum number of allowed
        """
        if len(self._graph.users[username].neighbor_anime) == 0:
            return []
        elif len(self._graph.users[username].neighbor_anime) < 3:
            return self.recommend_by_genres(username, limit)
        else:
            return self.recommend_by_users(username, limit)

    def recommend_by_genres(self, username: str, limit: int = 10) -> list[Anime]:
        """Returns a list of most matched anime in term of genres, up to a limit, sorted by match
        score and popularity, excluding the anime in the set exclusions."""
        user = self._graph.users[username]
        genres = user.best_liked_genres(5)
        matched_so_far = {}
        num_ani = len(self._graph.anime)
        exclusions = set(user.neighbor_anime.keys())
        for tup in genres:
            for anime in tup[0].neighbor_anime:
                if anime not in exclusions and anime.popularity is not None:
                    if anime in matched_so_far:
                        matched_so_far[anime] += (num_ani - anime.popularity) / 10 * tup[1]
                    else:
                        matched_so_far[anime] = (num_ani - anime.popularity) / 10 * tup[1]
        result_list = [(ani, matched_so_far[ani]) for ani in matched_so_far]
        result_list.sort(key=lambda x: x[1], reverse=True)
        if len(result_list) <= limit:
            return [ele[0] for ele in result_list]
        else:
            return [ele[0] for ele in result_list[:limit]]

    def recommend_by_users(self, username: str, limit: int = 10,
                           distant_measure: Union[Callable[[User, User], float], str] = 'custom') \
            -> list[Anime]:
        """Returns a list of anime recommendations, up to a limit, based on similar users.
        """
        user = self._graph.users[username]
        # By default, get 100 most similar users.
        exclusions = set(user.neighbor_anime.keys())
        similar_users = self._graph.most_similar_users(user, distant_measure, limit=100)
        recommended_so_far = set()
        result_list = []
        for user in similar_users:
            for anime in user.neighbor_anime:
                rating = user.neighbor_anime[anime]
                if anime not in exclusions and rating >= SCORE_FAVORITE and \
                        anime not in recommended_so_far:
                    recommended_so_far.add(anime)
                    # Adding like this keeps the most relevant recommendations to the start of the
                    # list.
                    result_list.append(anime)
                    if len(result_list) >= limit:
                        return result_list
        return result_list

    def recommend_by_score_prediction(self, username: str, limit: int = 10) -> list[Anime]:
        """Returns a list of anime recommendations, up to a limit, based on score predictions
        calculated from similar users."""
        user = self._graph.users[username]
        exclusions = set(user.neighbor_anime.keys())
        scores_so_far = []
        for anime in self._graph.anime.values():
            if anime not in exclusions:
                scores_so_far.append((anime, self.predict_review_score(user, anime)))
        scores_so_far.sort(key=lambda x: x[1], reverse=True)
        return [tup[0] for tup in scores_so_far[:limit]]

    def predict_review_score(self, user: User, anime: Anime) -> float:
        """Predict the score that the given user would give the given book.

        Preconditions:
            - user in self._graph.users
            - book in self._graph.
        """
        if user.adjacent(anime):
            return user.get_weight(anime)

        # Accumulators
        weighted_total_rating = 0.0
        total_weight = 0.0
        for other in anime.neighbor_users:
            score = 1 - jaccard_distance(user, other)  # Is the Jaccard similarity
            if score > 0.0:
                weighted_total_rating += other.get_weight(anime) * score
                total_weight += score

        if total_weight > 0:
            res = weighted_total_rating / total_weight
            if res == 10.0:
                print(anime)
            return res
        else:
            return anime.score if anime.score is not None else 0

    def visualize_graph(self, max_vertices: int = 10000) -> None:
        """Visualize the graph using networkx and plotly.
        Preconditions:
            - The graph has been loaded with the given data.
        """
        graph_visualization.visualize_graph(self._graph, max_vertices=max_vertices)
