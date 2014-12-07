"""
Road network formation
======================

The primary purpose of this model is to abstract a road connectivity network
from the complicated OSM raw GIS data. The network is going to be stored as a
NetworkX graph.

The nodes are going to be just the traffic junctions and the dead ends of the
road traffic system. And each node has the original id in the raw OSM data as
their identity, and the coordinate stored in the attribute ``coord``.

Each edge is going to be an undirected edge connecting the nodes. They all have
got the attribute of ``name`` for the name of the road, and the attribute of
``travel_time`` for the time needed to traverse the edge by a common traveller.

"""

import networkx as nx
from geopy.distance import vincenty


#
# Constants controlling the bahaviour of the code
# -----------------------------------------------
#

# if the ``highway`` key contains the follow value for a node in raw OSM, then
# it is considered a node in the network.
_NODES_TAGS = [
    'traffic_signals',
    'crossing',
    'turning_circle',
    'motorway_junction',
    ]

# The speed to travel on each kind of highways
# In miles per hour
_HIGHWAY_SPEEDS = {
    'residential': 20.0,
    'primary': 40.0,
    'primary_link': 40.0,
    'secondary': 35.0,
    'tertiary': 30.0,
    'footway': 35.0,
    'service': 35.0,
    'motorway': 70.0,
}


#
# Utility functions
# -----------------
#

def _test_if_node(node):

    """Tests if a node in the raw OSM data a node in the network"""

    tags = node.tags
    return 'highway' in tags and tags['highway'] in _NODES_TAGS


def _calc_distance(coord1, coord2):

    """Calculates the distance between two points

    A shallow wrapper of the geopy Vicinty distance calculator, returns the
    distance in miles.

    """

    return vincenty(coord1, coord2).miles


#
# The driver function
# -------------------
#

def form_network_from_osm(raw_osm):

    """Forms a road network from the raw OSM data

    :param raw_osm: A :py:class:`readosm.RawOSM` instance for the raw data
    :returns: A networkX graph for the road connectivity

    """

    net = nx.Graph()

    # nodes formation
    nodes = raw_osm.nodes
    for node_id, node in nodes.iteritems():
        if _test_if_node(node):
            net.add_node(node_id)
            net.node[node_id]['coord'] = node.coord
        continue

    # edge formation
    for way in raw_osm.ways.itervalues():

        # test if it is actually a road
        tags = way.tags
        if 'highway' in tags:
            highway = tags['highway']
        else:
            continue  # building or something like that

        # connect the nodes in the network

        prev_node_id = None  # The previous node in the network
        # The coordinate of the previous raw node in the OSM data
        prev_coord = way.nodes[0].coord
        distance = 0.0

        for node_id in way.nodes:
            node = nodes[node_id]

            # Update the distance
            curr_coord = node.coord
            distance += _calc_distance(curr_coord, prev_coord)
            prev_coord = curr_coord

            if _test_if_node(node):
                # add edge if there is a previous node
                if prev_node_id is not None:
                    # Add the new edge
                    try:
                        travel_time = distance / _HIGHWAY_SPEEDS[highway]
                    except IndexError:
                        raise IndexError(
                            'Unknown highway type %s' % highway
                            )
                    net.add_edge(
                        node_id, prev_node_id,
                        travel_time=travel_time,
                        name=tags.get('name', '')
                        )
                # Update previous node no matter there is a previous one
                prev_node_id = node_id
                distance = 0.0

    return net
