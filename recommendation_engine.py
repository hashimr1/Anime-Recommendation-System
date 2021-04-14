"""CSC111 Final Project: My Anime Recommendations
===============================================================
The recommendation_engine module.

This module contains the definition of the RecommendationEngine
class and its related function implementations.
================================================================
@author: Tu Pham
"""

from __future__ import annotations
from typing import Optional
from anime_graph import AnimeGraph, Anime, Genre, User
import graph_visualization
import csv

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
    _current_user: Optional[User]

    def __init__(self, graph: AnimeGraph) -> None:
        """Initializing the Engine."""
        self._graph = graph
        self._current_user = None
        self._anime_name_map = {}
        for anime in self._graph.anime.values():
            self._anime_name_map[anime.title] = anime

    def log_in(self, username) -> bool:
        """Log a user into the system.
        Returns whether the log in is successful. It is unsuccessful when there is already
        an user logged in, or there is no user with the matching username.
        """
        if self._current_user is None and username in self._graph.users:
            self._current_user = self._graph.users[username]
            return True
        else:
            return False

    def log_out(self) -> bool:
        """Log out for the user currently logging in.
        Returns whether the log out attempt is successful. When there is no user currently
        logged in, it returns False.
        """
        if self._current_user is not None:
            self._current_user = None
            return True
        else:
            return False

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

    def add_review(self, anime_uid: int, review_score: float, reviews_filepath: str) -> None:
        """Add a review to the database and the graph.
            - username in self._graph
            - anime in self._graph
        """
        if self._current_user is None:
            return
        # String form of the score
        s = str(review_score)
        # For now we don't use the details of categorized score yet
        pseudo_details = {'Overall': s, 'Story': s, 'Animation': s, 'Sound': s,
                          'Character': s, 'Enjoyment': s}
        # The '0' is a temporary review ID, we don't need it for now.
        new_row = ['0', self._current_user.username, anime_uid, s, pseudo_details]
        with open(reviews_filepath, 'a+', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerow(new_row)
        # This will overwrite the current user-anime edge, if there is any.
        self._graph.add_review(self._current_user.username, anime_uid, review_score)

    def fetch_new_anime(self, limit=10) -> list[Anime]:
        """Returns a list of newly released anime, up to a limit."""
        return self._graph.fetch_new_anime(limit)

    def fetch_anime_by_name(self, name: str) -> Optional[Anime]:
        """Returns an anime in the system.
        If there is none, returns None."""
        return self._graph.fetch_anime_by_name(name)

    def fetch_popular_anime(self, limit=10) -> list[Anime]:
        """Returns a list of most popular anime, up to a limit"""
        return self._graph.fetch_popular_anime(limit)

    def fetch_popular_by_genre(self, genre: str, limit=10) -> list[Anime]:
        """Returns a list of most popular anime of a given genre, up to a limit."""
        return self._graph.fetch_popular_by_genre(genre, limit)

    def fetch_all_genres(self) -> list[str]:
        """Return the list of all anime genres, sorted in alphabetical order."""
        return self._graph.fetch_all_genres()

    def recommend(self, limit: int = 10) -> list[Anime]:
        """Returns a list of anime for the currently logged in user, as suggestions.
        Returns an empty list if the user has not reviewed any anime.
        Function Parameters:
            - limit: the maximum number of allowed
        Preconditions:
            - self._current_user is not None
        """
        exclusions = set(self._current_user.neighbor_anime.keys())
        if len(self._current_user.neighbor_anime) == 0:
            return []
        elif len(self._current_user.neighbor_anime) < 3:
            # Get the 5 most liked genres for content filtering
            liked_genres = self._current_user.best_liked_genres(5)
            return self._recommend_by_genres(liked_genres, limit, exclusions)
        else:
            # By default, get 50 most similar users.
            similar_users = self._current_user.most_similar_users()
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

    def visualize_graph(self, max_vertices: int = 10000) -> None:
        """Visualize the graph using networkx and plotly.
        Preconditions:
            - The graph has been loaded with the given data.
        """
        graph_visualization.visualize_graph(self._graph, max_vertices=max_vertices)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': [],  # the names (strs) of imported modules
        'allowed-io': [],  # the names (strs) of functions that call print/open/input
        'max-line-length': 100,
        'disable': ['E1136']
    })
    # engine = RecommendationEngine("Data/animes.csv", 'Data/profiles.csv', 'Data/reviews.csv')
