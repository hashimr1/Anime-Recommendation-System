"""CSC111 Final Project: My Anime Recommendations
===============================================================================
The distance_measures module.
###############################################################################
# ================= Measures of distance between two users ================== #
###############################################################################
The higher the distance between two users is, the less similar they are.
===============================================================================
@author: Tu Pham
"""
from math import *
from decimal import Decimal
from anime_graph import User, Anime


def euclidean_distance(user1: User, user2: User) -> float:
    """Returns the euclidean distance between two User vertices.
    """
    common_animes = set.intersection(set(user1.neighbor_anime.keys()),
                                     set(user2.neighbor_anime.keys()))
    return sqrt(sum(pow(anime.neighbor_users[user1] - anime.neighbor_users[user2], 2)
                    for anime in common_animes))


def manhattan_distance(user1: User, user2: User) -> float:
    """Return the manhattan distance between two User vertices"""
    common_animes = set.intersection(set(user1.neighbor_anime.keys()),
                                     set(user2.neighbor_anime.keys()))
    return sum(abs(anime.neighbor_users[user1] - anime.neighbor_users[user2])
               for anime in common_animes)


def minkowski_distance(user1: User, user2: User) -> float:
    """Return the minkowski distance between two lists """
    # predefined p_value
    p_value = 3
    common_animes = set.intersection(set(user1.neighbor_anime.keys()),
                                     set(user2.neighbor_anime.keys()))
    return _nth_root(sum(pow(abs(anime.neighbor_users[user1] - anime.neighbor_users[user2]),
                             p_value) for anime in common_animes), p_value)


def _nth_root(value, n_root) -> float:
    """Return the n_root of an value."""

    root_value = 1 / float(n_root)
    return Decimal(value) ** Decimal(root_value)


def cosine_distance(user1: User, user2: User) -> float:
    """ return cosine similarity between two lists """
    common_animes = set.intersection(set(user1.neighbor_anime.keys()),
                                     set(user2.neighbor_anime.keys()))
    if len(common_animes) == 0:
        return 1
    numerator = sum(anime.neighbor_users[user1] * anime.neighbor_users[user2]
                    for anime in common_animes)
    denominator = _square_rooted(user1, common_animes) * _square_rooted(user2, common_animes)
    try:
        return 1 - (numerator / denominator)
    except ZeroDivisionError:
        print(user1.username)
        for anime in common_animes:
            print(anime.neighbor_users[user1])
        print(user2.username)
        for anime in common_animes:
            print(anime.neighbor_users[user2])
        return 1


def _square_rooted(user: User, animes: set[Anime]) -> float:
    """Return the square rooted value of the sum of squares of user review scores."""

    return sqrt(sum([anime.neighbor_users[user] * anime.neighbor_users[user]
                     for anime in animes]))


def jaccard_distance(user1: User, user2: User) -> float:
    """Returns the Jaccard similarity between two lists """
    jaccard_similarity = 0.0
    if len(user1.neighbor_anime) > 0 and len(user2.neighbor_anime) > 0:
        # Accumulators: the number of shared neighbours and shared neighbours with same edge
        # weight.
        common_count = 0
        strict_count = 0
        for key in user1.neighbor_anime:
            if key in user2.neighbor_anime:
                common_count += 1
                strict_count += int(user1.neighbor_anime[key] == user2.neighbor_anime[key])
        jaccard_similarity = strict_count / \
            (len(user1.neighbor_anime) + len(user2.neighbor_anime) - common_count)

    return 1 - jaccard_similarity
