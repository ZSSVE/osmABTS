"""
The model class definition
==========================

A model is a complete model that is able to be simulated. It is the top most
class in this project and is the one that mostly interacts with the users.

"""

class Model(object):

    """Complete models for the simulation

    This is the primary class of this library and offers most of its user
    interface. As a result, a simultion would primarily consist of interacting
    with its instances. The major steps of the simulation and the major fields
    of this class goes as follows.

    Simulation preparation
    ----------------------

    First a road network from the simplification of the actual OSM data is
    formed as a networkx graph. The nodes are just the traffic junctions and
    the edges are the road connections, with travelling time given as the
    weight. This network can be formed by calling the :py:meth:`form_network`
    method and stored in the :py:attr:`network` field.

    Next the places of interest for the travellers to visit needs to be
    generated, also from the OSM data. To make the problem simple, the places
    are all rounded to the nearest traffic junction. And it is stored in the
    attribute :py:attr:`places` as dictionary with the place category as key,
    and list of the actual places as entries. It can be formed from the
    :py:meth:`form_stage` method.

    Then comes the most important part, the generation of the agents of the
    simulation, travellers. Each traveller will has got a set of attributes,
    like the home location and work place. The list of travellers are stored in
    the attribute :py:attr:`travellers` and formed by calling the method
    :py:meth:`form_travellers`.

    Note that the network, stage, and travellers have got dependency on their
    predecessors so they need to be formed consecutively.

    Simulation
    ----------

    After the preparation on the fields :py:attr:`network`, :py:attr:`stage`,
    and :py:attr:`travellers`, the actual simulation can be started. Note that
    in the current simple mode, the simulation will primarily just consists of
    the generation of a large set of trips based on the agents' activity and
    the computation of the total (average) travel time for the agents based on
    a shortest path algorithm.

    The generation of the trips can be achieved by calling the method
    :py:meth:`gen_trips` and the trips will be stored in the :py:attr:`trips`
    attribute with the initial and final node pair as elements. Then the
    computation of the shortest paths can be achieved by
    :py:meth:`compute_paths` and stored in the attribute :py:attr:`paths`.
    Finally the average time spent on travel can be computed by the
    straightforward method :py:meth:`compute_mean_time`.

    """

    __slots__ = [
        'network',
        'places',
        'travellers',
        'trips',
        'paths',
        ]

