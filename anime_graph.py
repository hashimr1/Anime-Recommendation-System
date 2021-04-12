"""CSC111 Final Project: My Anime Recommendations
===============================================================
The anime_graph module.

This module contains the definition of the AnimeGraph class
and its related function implementations.
================================================================
@author: Tu Pham
"""
from __future__ import annotations

from typing import Union, Optional
import networkx as nx


class Vertex:
    """Abstract class for a vertex in the graph"""


class User(Vertex):
    """An user of the anime streaming service.

    Instance Attributes:
        - username: A string. The username of this user.
        - gender: A string or None. The gender of the user.
        - birth_year: An int or None. The birth year of the user. We only takes the
        birth year into account right now for simplicity, since the birth year matter the most
        in determining age-related similarities between user.
    """

    username: str
    gender: Optional[str]
    birth_year: Optional[int]

    neighbor_anime: dict[Anime, Union[int, float]]
    neighbor_genres: dict[Genre, Union[int, float]]

    def __init__(self, username: str, gender: Optional[str],
                 birth_year: Optional[int]) -> None:
        """Initialize an user vertex"""
        self.username = username
        self.gender = gender
        self.birth_year = birth_year
        # self.favorites_anime = favorites_anime if favorites_anime is not None else set()

        self.neighbor_anime = {}
        self.neighbor_genres = {}

    def __str__(self) -> str:
        """Returns the user name."""
        return self.username

    def __hash__(self) -> int:
        """Returns the hash value of this user."""
        return hash(self.username)

    def __eq__(self, other: Vertex) -> bool:
        """Returns whether this vertex is equal to another vertex."""
        if not isinstance(other, Vertex):
            raise TypeError(f'Equality is undefined between instances '
                            f'of {type(self)} and {type(other)}')
        elif isinstance(other, User):
            return self.username == other.username
        else:
            return False

    def most_similar_users(self, limit: int = 50) -> list[tuple[User, float]]:
        """Returns a list tuples of most similar users, up to a limit, based on user reviews.
        Each tuple takes the form (a, b), where a is the User object, and b is the similarity
        score.
        """
        # Accumulator:
        similarity_map = {}
        for anime in self.neighbor_anime:
            for other in anime.neighbor_users:
                if other is not self:
                    difference = abs(self.neighbor_anime[anime] - other.neighbor_anime[anime])
                    value_to_add = 5.5 - difference  # Negative when difference > 5.5
                    if other in similarity_map:
                        similarity_map[other] += value_to_add
                    else:
                        similarity_map[other] = value_to_add
        resulting_list = [(user, similarity_map[user]) for user in similarity_map if
                          similarity_map[user] > 0]

        if len(resulting_list) <= limit:
            return resulting_list
        else:
            resulting_list.sort(key=lambda x: x[1], reverse=True)
            return resulting_list[:limit]

    def best_liked_genres(self, limit: int = 5) -> list[tuple[Genre, float]]:
        """Returns a list tuples (a, b), where a is the genre the user like and b is the
        liking score of the user toward that genre. The list contains the <limit> most liked
        genres by the user.
        """
        liked_list = [(genre, self.neighbor_genres[genre]) for genre in self.neighbor_genres if
                      self.neighbor_genres[genre] > 0]
        if len(liked_list) <= limit:
            return liked_list
        else:
            liked_list.sort(key=lambda x: x[1], reverse=True)
            return liked_list[:limit]


class Anime(Vertex):
    """An anime in the graph.

    Instance Attributes:
        - uid: The unique numeric id of the anime.
        - title: The title of the anime.
        - synopsis: A paragraph description of the anime.
        - total_episodes: The number of episodes of the anime.
        - popularity: The ranking in popularity. The lower the number, the higher the rank.
        - rank: MyAnimeList ranking
        - score: MyAnimeList score
    """

    uid: int
    title: str
    synopsis: str
    total_episodes: int
    popularity: Optional[int]
    rank: Optional[int]
    score: Optional[float]

    neighbor_genres: set  # The set of Genres
    neighbor_users: dict[User, Union[float, int]]

    def __init__(self, uid: int, title: str, synopsis: str,
                 total_episodes: int, popularity: Optional[int],
                 rank: Optional[int], score: Optional[int]) -> None:
        """Initializer"""
        self.uid = uid
        self.title = title
        self.total_episodes = total_episodes
        self.popularity = popularity
        self.rank = rank
        self.score = score
        self.synopsis = synopsis
        self.neighbor_genres = set()
        self.neighbor_users = {}

    def __str__(self) -> str:
        """Returns the title of the anime."""
        return self.title

    def __hash__(self) -> int:
        """Returns the hash value of this user."""
        return hash(self.uid)

    def __eq__(self, other: Vertex) -> bool:
        """Returns whether this vertex is equal to another vertex."""
        if not isinstance(other, Vertex):
            raise TypeError(f'Equality is undefined between instances '
                            f'of {type(self)} and {type(other)}')
        elif isinstance(other, Anime):
            return self.uid == other.uid

        else:
            return False


class Genre(Vertex):
    """A genre in the anime categorization system"""

    genre_name: str
    neighbor_anime: set[Anime]  # The set of anime IDs in this genre
    neighbor_users: dict[User, Union[float, int]]

    def __init__(self, name: str) -> None:
        self.genre_name = name
        self.neighbor_anime = set()
        self.neighbor_users = {}

    def __str__(self) -> str:
        """Returns the string representation of the genre."""
        return self.genre_name

    def __hash__(self) -> int:
        """Returns the hash value of this user."""
        return hash(self.genre_name)

    def __eq__(self, other: Vertex) -> bool:
        """Returns whether this vertex is equal to another vertex."""
        if not isinstance(other, Vertex):
            raise TypeError(f'Equality is undefined between instances '
                            f'of {type(self)} and {type(other)}')
        elif isinstance(other, Genre):
            return self.genre_name == other.genre_name
        else:
            return False


class AnimeGraph:
    """A weighted graph, consisting of Anime, Users and Genres.

    Instance Attributes:
        -
    """

    users: dict[str, User]
    genres: dict[str, Genre]
    anime: dict[int, Anime]

    def __init__(self) -> None:
        """Initialize an instance of the AnimeGraph class"""
        self.users = {}
        self.anime = {}
        self.genres = {}

    def add_anime(self, uid: int, title: str, synopsis: str,
                  total_episodes: int, popularity: Optional[int],
                  rank: Optional[int], score: Optional[int]) -> None:
        """Add a new Anime to the graph.
        If the Anime is already in the graph, does nothing."""

        if uid not in self.anime:
            new_anime = Anime(uid, title, synopsis, total_episodes,
                              popularity, rank, score)
            self.anime[uid] = new_anime

    def _add_genre(self, genre_name: str) -> None:
        """Add a new anime genre to the graph.
        If the genre is already in the graph, does nothing.

        Preconditions:
            - genre_name not in self._genres
        """
        new_genre = Genre(genre_name)
        self.genres[genre_name] = new_genre

    def add_user(self, username: str, gender: Optional[str],
                 birth_year: Optional[int]) -> None:
        """Add a new user to the graph.
        If the user is already in the graph, does nothing. """

        if username not in self.users:
            new_user = User(username, gender, birth_year)
            self.users[username] = new_user

    def add_review(self, username: str, anime_uid: int, score: Union[int, float]) -> None:
        """Add a review to the graph by establishing a weighted edge between
        an anime and a user.
        This function also establish weighted edges between the user and the related genres.
        If there is already an edge between the user and the given genre, the weight will change
        based on the score."""

        if username in self.users and anime_uid in self.anime:
            user = self.users[username]
            anime = self.anime[anime_uid]

            user.neighbor_anime[anime] = score
            anime.neighbor_users[user] = score

            for genre in anime.neighbor_genres:
                deviation = (score - 5.5)
                if genre in user.neighbor_genres:
                    user.neighbor_genres[genre] += deviation
                    genre.neighbor_users[user] += deviation
                else:
                    user.neighbor_genres[genre] = deviation
                    genre.neighbor_users[user] = deviation

    def add_anime_genre_edge(self, anime_uid: int, genre_name: str) -> None:
        """Add an anime-genre edge to the graph."""
        if anime_uid in self.anime:
            if genre_name not in self.genres:
                self._add_genre(genre_name)

            self.anime[anime_uid].neighbor_genres.add(self.genres[genre_name])
            self.genres[genre_name].neighbor_anime.add(self.anime[anime_uid])
        else:
            raise ValueError

    def to_networkx(self, max_vertices: int = 10000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note that this method is provided for you, and you shouldn't change it.
        """
        graph_nx = nx.Graph()
        for anime in self.anime.values():
            graph_nx.add_node(anime, kind='anime')

            for genre in anime.neighbor_genres:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(genre, kind='genre')

                if genre in graph_nx.nodes:
                    graph_nx.add_edge(anime, genre)

            for user in anime.neighbor_users:
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(user, kind='user')

                if user in graph_nx.nodes:
                    graph_nx.add_edge(anime, user)

            if graph_nx.number_of_nodes() >= max_vertices:
                break

        return graph_nx
