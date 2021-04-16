"""CSC111 Winter 2021 Assignment 3: Graphs, Recommender Systems, and Clustering (Visualization)

Module Description
==================

This module contains some Python functions that you can use to visualize the graphs
you're working with on this assignment. You should not modify anything in this file.
It will not be submitted for grading.

Disclaimer: we didn't have time to make this file fully PythonTA-compliant!

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2021 David Liu and Isaac Waller.
"""
import networkx as nx
from plotly.graph_objs import Scatter, Figure
import anime_graph
import plotly.express as px

# Colours to use when visualizing different clusters.
COLOUR_SCHEME = [
    '#2E91E5', '#E15F99', '#1CA71C', '#FB0D0D', '#DA16FF', '#222A2A', '#B68100',
    '#750D86', '#EB663B', '#511CFB', '#00A08B', '#FB00D1', '#FC0080', '#B2828D',
    '#6C7C32', '#778AAE', '#862A16', '#A777F1', '#620042', '#1616A7', '#DA60CA',
    '#6C4516', '#0D2A63', '#AF0038'
]

LINE_COLOUR = 'rgb(210,210,210)'
VERTEX_BORDER_COLOUR = 'rgb(50, 50, 50)'
ANIME_COLOUR = 'rgb(89, 205, 105)'
USER_COLOUR = 'rgb(105, 89, 205)'
GENRE_COLOUR = 'rgb(205, 105, 89)'


def visualize_graph(graph: anime_graph.AnimeGraph,
                    layout: str = 'spring_layout',
                    max_vertices: int = 10000,
                    output_file: str = '') -> None:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
        - layout: which graph layout algorithm to use
        - max_vertices: the maximum number of vertices that can appear in the graph
        - output_file: a filename to save the plotly image to (rather than displaying
            in your web browser)
    """
    graph_nx = graph.to_networkx(max_vertices)

    pos = getattr(nx, layout)(graph_nx)

    x_values = [pos[k][0] for k in graph_nx.nodes]
    y_values = [pos[k][1] for k in graph_nx.nodes]
    labels = list(graph_nx.nodes)
    sizes = [10 if graph_nx.nodes[k]['kind'] == 'genre' else 5 for k in graph_nx.nodes]
    kinds = [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes]

    colours = [ANIME_COLOUR if kind == 'anime'
               else USER_COLOUR if kind == 'user' else GENRE_COLOUR for kind in kinds]

    x_edges = []
    y_edges = []
    for edge in graph_nx.edges:
        x_edges += [pos[edge[0]][0], pos[edge[1]][0], None]
        y_edges += [pos[edge[0]][1], pos[edge[1]][1], None]

    trace3 = Scatter(x=x_edges,
                     y=y_edges,
                     mode='lines',
                     name='edges',
                     line=dict(color=LINE_COLOUR, width=1),
                     hoverinfo='none',
                     )
    trace4 = Scatter(x=x_values,
                     y=y_values,
                     mode='markers',
                     name='nodes',
                     marker=dict(symbol='circle-dot',
                                 size=sizes,
                                 color=colours,
                                 line=dict(color=VERTEX_BORDER_COLOUR, width=0.5)
                                 ),
                     text=labels,
                     hovertemplate='%{text}',
                     hoverlabel={'namelength': 0}
                     )

    data1 = [trace3, trace4]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


###############################################################################
# ========================= Custom functions ================================ #
###############################################################################
def present_evaluation_chart(eval_data: list[tuple[str, float]], type_of_eval: str) -> None:
    """Show a bar chart on browser, which illustrate the efficiency of recommendation methods.
    Each tuple in the input list contains the name of the method of measuring the proximity
    between users and the number of correct guesses it makes.
    Preconditions:
        - type_of_eval in {'accuracy', 'running time'}
    """
    title = "The Number of correct guesses for the favorite animes of 300 users, using" \
            "different measures of User vertex proximity." if type_of_eval == 'accuracy' \
        else "Running times for generating recommendations for 300 users, using different " \
            "measures of User vertex proximity."
    method_names = [tup[0] for tup in eval_data]
    quantities = [tup[1] for tup in eval_data]
    y_title = type_of_eval.capitalize()
    data_map = {'Measure': method_names, y_title: quantities}
    fig = px.bar(data_map, x='Measure', y=y_title, title=title)
    fig.show()
