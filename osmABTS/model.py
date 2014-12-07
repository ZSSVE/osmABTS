"""
The model class definition
==========================

A *model* here is a complete model that is able to be simulated. It is the top
most class in this project and is the one that mostly interacts with the users.

"""

from .readosm import read_osm
from .network import form_network_from_osm
from .places import form_places_from_osm
from .travellers import Traveller
from .trips import gen_trips, DEFAULT_TRIPS
from .paths import ShortestPath


class Model(object):

    """Complete models for the simulation

    This is the primary class of this library and offers most of its user
    interface. As a result, a simultion would primarily consist of interacting
    with its instances. The major steps of the simulation and the major fields
    of this class goes as follows.

    OpenStreetMap data parsing
    --------------------------

    Before everything, the data from the OpenStreetMap website need to be
    parsed into a simpler data structure. It can be finished by giving a file
    name for the XML data file to the constructor. And the parsed results will
    be stored in the :py:attr:`raw_osm` attribute.

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
    and list of the actual nodes as entries. It can be formed from the
    :py:meth:`form_places` method.

    Then comes the most important part, the generation of the agents of the
    simulation, travellers. Each traveller will has got a set of attributes,
    like the home location and work place. The list of travellers are stored in
    the attribute :py:attr:`travellers` and formed by calling the method
    :py:meth:`form_travellers`.

    Note that the network, stage, and travellers have got dependency on their
    predecessors so they need to be formed consecutively.

    Simulation
    ----------

    After the preparation on the fields :py:attr:`network`, :py:attr:`places`,
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
        'raw_osm',
        'network',
        'places',
        'travellers',
        'trips',
        'time_span',
        'paths',
        ]

    def __init__(self, osm_file):

        """Initializes the object with given OpenStreetMap data

        :param osm_file: The file name for the OpenStreetMap data
        :raises ValueError: If the file is corrupt or cannot be read
        """

        self.raw_osm = read_osm(osm_file)

        # Initialize the fields to None for detection of no value yet computed
        self.network = None
        self.places = None
        self.travellers = None
        self.trips = None
        self.paths = None

    def form_network(self):

        """Forms the road network based on the raw data """

        self.network = form_network_from_osm(self.raw_osm)

    def form_places(self):

        """Forms the dictionary of interesting places"""

        if self.network is None:
            raise ValueError('Places cannot be generated without a network')

        self.places = form_places_from_osm(self.raw_osm)

    def form_travellers(self, number):

        """Forms a list of travellers

        :param number: The number of travellers to form

        """

        if self.network is None:
            raise ValueError('Network unavailable for traveller generation')
        if self.places is None:
            raise ValueError('Places unavailable for traveller generation')

        self.travellers = [
            Traveller(self.network, self.places)
            for _ in xrange(0, number)
            ]

    def gen_trips(self, time_span, trips=None):

        """Generates trips for the simulation

        :param time_span: The time span for the simulation, in weeks
        :param trips: A list of :py:class:`trips.Trip` objects for the trip
            generation. It can be omitted to use the default trip list.

        """

        trips = trips or DEFAULT_TRIPS

        if self.network is None:
            raise ValueError('Network unavailable for trip generation')
        if self.places is None:
            raise ValueError('Places unavailable for trip generation')
        if self.travellers is None:
            raise ValueError('Travellers unavailable for trip generation')

        self.time_span = time_span
        self.trips = []
        for traveller_i in self.travellers:
            self.trips.extend(gen_trips(
                time_span, self.network, self.places, trips, traveller_i
                ))

    def compute_paths(self):

        """Computes the shortest paths for the trips"""

        if self.trips is None:
            raise ValueError('Trips unavailable for shortest path computing')

        self.paths = [
            ShortestPath(self.network, trip_i)
            for trip_i in self.trips
            ]

    def compute_mean_time(self):

        """Computes the mean travel time for the travellers

        :returns: The mean travel time for all travellers in one unit of time

        """

        if self.paths is None:
            raise ValueError('Paths unavailable for mean travel time')
        return sum(
            path_i.travel_time for path_i in self.paths
            ) // len(self.paths) / self.time_span
