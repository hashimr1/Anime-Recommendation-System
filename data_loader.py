"""CSC111 Final Project: My Anime Recommendations
===============================================================
The data_loader module.

This module contains functions to create an AnimeGraph from the
datafiles as described in the report.
================================================================
@author: Tu Pham
"""
import csv
from anime_graph import AnimeGraph
from datetime import datetime


def create_anime_graph_from_data(anime_filepath: str, user_profile_filepath: str,
                                 review_filepath: str) -> AnimeGraph:
    """Create an AnimeGraph from the given data files.
    Preconditions:
        - The data files follow the format as described in the report.
    """
    graph = AnimeGraph()
    _load_anime_data(graph, anime_filepath)
    _load_user_data(graph, user_profile_filepath)
    _load_review_data(graph, review_filepath)
    return graph


def _load_anime_data(graph: AnimeGraph, filepath: str) -> None:
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
            graph.add_anime(uid=row[0], title=row[1], synopsis=row[2], aired_date=row[4],
                            total_episodes=row[5], popularity=row[7],
                            rank=row[8], score=row[9], image_url=row[10])
            genres = row[3][2:-2].split('\', \'')
            for genre in genres:
                if genre != '':
                    graph.add_anime_genre_edge(int(row[0]), genre)


def _load_user_data(graph: AnimeGraph, filepath: str) -> None:
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
            graph.add_user(row[0], row[1], row[2])
            for fav_uid in row[3]:  # row 3 contains a list of favorite anime uid.
                # giving a default score of 9 to a favorite anime
                graph.add_review(row[0], fav_uid, 9)


def _load_review_data(graph: AnimeGraph, filepath: str) -> None:
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
            graph.add_review(row[1], int(row[2]), float(row[3]))


def _convert_anime_row_data_types(row: list) -> None:
    """Convert a row in the csv reader to the usable format by mutating this row.
    This means:
        - row[0] is an int
        - row[1] is a str
        - row[2] is a str
        - row[4] is a datetime object
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

    try:
        row[4] = datetime.strptime(row[4][-12:].lstrip(), '%b %d, %Y')
    except ValueError:
        try:
            row[4] = datetime.strptime(row[4][-9:], '%b, %Y')
        except ValueError:
            try:
                row[4] = datetime.strptime(row[4][:12].rstrip(), '%b %d, %Y')
            except ValueError:
                try:
                    row[4] = datetime.strptime(row[4][:4].rstrip(), '%Y')
                except ValueError:
                    # Meaning the anime airing date is not available.
                    # Making 1900 the default year help sorting easier.
                    row[4] = datetime(year=1900, month=1, day=1)

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


def user_test_data_extract(profiles_filepath: str, num_to_extract: int) -> None:
    """Separate the profiles data into two new files. One contains some extracted user profiles
    with a part of their liked anime. The other contains those profiles with the remaining
    liked anime.
    This functions is intended to be run on the original data test.
    """
    extracted_so_far = 0
    with open(profiles_filepath) as fp_in, \
            open('Data/profiles_removed.csv', 'w', newline='') as fp_out1, \
            open('Data/profiles_extracted.csv', 'w', newline='') as fp_out2:
        reader = csv.reader(fp_in)
        writer1 = csv.writer(fp_out1, delimiter=",")
        writer2 = csv.writer(fp_out2, delimiter=",")

        for row in reader:
            temp = row[3][2:-2].split('\', \'')
            if len(temp) >= 9 and extracted_so_far < num_to_extract:
                pivot_index = int(len(temp) * 1 / 3)
                keep = temp[:pivot_index]
                extract = temp[pivot_index:]
                row[3] = str(keep)
                writer1.writerow(row)
                row[3] = str(extract)
                writer2.writerow(row)
                extracted_so_far += 1
            else:
                writer1.writerow(row)
    remove_user_liked_reviews('Data/profiles_extracted.csv', 'Data/reviews.csv')


def remove_user_liked_reviews(extracted_users_filepath: str, review_filepath: str) -> None:
    """Opens the reviews file. Delete all the reviews about the user's liked anime."""
    # A mapping of username to their list of liked anime
    user_like_lists = {}

    with open(extracted_users_filepath) as fp_in:
        reader = csv.reader(fp_in)

        for row in reader:
            user_like_lists[row[0]] = row[3][2:-2].split('\', \'')

    with open(review_filepath) as fp_in, open('removed_reviews.csv', 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")

        for row in reader:
            if row[1] not in user_like_lists or row[2] not in user_like_lists[row[1]]:
                writer.writerow(row)


# Functions to make the data cleaner
def remove_repeated_profiles(profiles_filepath: str) -> None:
    """Create a new profiles file with no repeated row"""
    usernames = set()
    with open(profiles_filepath) as fp_in, open('cleaned_profiles.csv', 'w', newline='') as fp_out:
        reader = csv.reader(fp_in)
        writer = csv.writer(fp_out, delimiter=",")

        for row in reader:
            if row[0] not in usernames:
                usernames.add(row[0])
                writer.writerow(row)
