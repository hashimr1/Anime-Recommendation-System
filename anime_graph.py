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


class Anime(Vertex):
    """An anime in the graph.

    Instance Attributes:
        - uid: The unique numeric id of the anime.
        - title: The title of the anime.
        - synopsis: A paragraph description of the anime.
        - total_episodes: The number of episodes of the anime.
        - popularity: The ranking in popularity
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

    _users: dict[str, User]
    _genres: dict[str, Genre]
    _anime: dict[int, Anime]

    def __init__(self) -> None:
        """Initialize an instance of the AnimeGraph class"""
        self._users = {}
        self._anime = {}
        self._genres = {}

    def add_anime(self, uid: int, title: str, synopsis: str,
                  total_episodes: int, popularity: Optional[int],
                  rank: Optional[int], score: Optional[int]) -> None:
        """Add a new Anime to the graph.
        If the Anime is already in the graph, does nothing."""

        if uid not in self._anime:
            new_anime = Anime(uid, title, synopsis, total_episodes,
                              popularity, rank, score)
            self._anime[uid] = new_anime

    def _add_genre(self, genre_name: str) -> None:
        """Add a new anime genre to the graph.
        If the genre is already in the graph, does nothing.

        Preconditions:
            - genre_name not in self._genres
        """
        new_genre = Genre(genre_name)
        self._genres[genre_name] = new_genre

    def add_user(self, username: str, gender: Optional[str],
                 birth_year: Optional[int]) -> None:
        """Add a new user to the graph.
        If the user is already in the graph, does nothing. """

        if username not in self._users:
            new_user = User(username, gender, birth_year)
            self._users[username] = new_user

    def add_review(self, username: str, anime_uid: int, score: Union[int, float]) -> None:
        """Add a review to the graph.
        A review is a weighted edge between an anime and a user."""

        if username in self._users and anime_uid in self._anime:
            user = self._users[username]
            anime = self._anime[anime_uid]

            user.neighbor_anime[anime] = score
            anime.neighbor_users[user] = score

    def add_anime_genre_edge(self, anime_uid: int, genre_name: str) -> None:
        """Add an anime-genre edge to the graph."""
        if anime_uid in self._anime:
            if genre_name not in self._genres:
                self._add_genre(genre_name)

            self._anime[anime_uid].neighbor_genres.add(self._genres[genre_name])
            self._genres[genre_name].neighbor_anime.add(self._anime[anime_uid])
        else:
            raise ValueError

    def to_networkx(self, max_vertices: int = 10000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)

        Note that this method is provided for you, and you shouldn't change it.
        """
        graph_nx = nx.Graph()
        for anime in self._anime.values():
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
