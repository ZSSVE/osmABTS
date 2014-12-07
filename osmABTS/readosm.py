"""
OpenStreetMap XML file parsing
==============================

This module defined classes for nodes, ways and a shallow data structure for
all of these raw information from OSM XML file, as well as a parser based on
the standard expat library.

"""

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-branches

import xml.parsers.expat as expat


#
# Class definitions
# -----------------
#

class Node(object):

    """Nodes in the OSM XML file

    It mainly consists of the following attributes,

    .. py:attribute:: coord

        The coordinates for the node, in latitudes and longitudes.

    .. py:attribute:: tags

        A dictionary for the tags, using the same key and value as in the XML
        file.

    """

    __slots__ = [
        "coord",
        "tags",
        ]

    def __init__(self, attrs):

        """Initializes a node based on the attributes in XML

        The coordinates are going to be set, with the tags initialized to an
        empty dictionary.

        """

        self.coord = (
            float(attrs['lat']),
            float(attrs['lon']),
            )
        self.tags = {}


class Way(object):

    """Ways from the OSM XML file

    It primarily consists of the following attributes

    .. py:attribute:: nodes

        A list of identity references for the nodes

    .. py:attribute:: tags

        The tags dictionary, the same as that for the nodes

    """

    __slots__ = [
        "nodes",
        "tags",
        ]

    def __init__(self):

        """Initializes an instance

        The initialization is going to be trivial, just the lists and
        dictionaries set to empty ones.

        """

        self.nodes = []
        self.tags = {}


class RawOSM(object):

    """Raw GIS data from OpenStreetMap

    The XML input is going to be parsed into an instance of this project. The
    primary fields are

    .. py:attribute:: nodes

        A dictionary of nodes, with the identity integer as the key as the
        :py:class:`Node` instances as values.

    .. py:attribute:: ways

        A similar dictionary of ways, with identity as the key and the
        :py:class:`Way` instances as the values.

    """

    __slots__ = [
        "nodes",
        "ways",
        ]

    def __init__(self):

        """Initializes the instance

        It just sets the two dictionaries into empty ones.

        """

        self.nodes = {}
        self.ways = {}


#
# The parser function
# -------------------
#

def read_osm(file_name):

    """Reads the OSM XML file with given name

    :param file_name: The name of the OSM XML file
    :returns: A :py:class:`RawOSM` instance for the data
    :raises: :py:exc:`ValueError` if something went wrong

    """

    raw_osm = RawOSM()

    # The current state, to be used as a stack
    # Its entries should be pair of element id and element for nodes and ways
    current_state = []

    # The closures for the call-backs

    def start_element(name, attrs):

        """Call-back at the start of element"""

        # At top level
        if name == 'osm':
            pass
        # For a node
        elif name == 'node':
            current_state.append(
                (int(attrs['id']), Node(attrs))
                )
        # For a way
        elif name == 'way':
            current_state.append(
                (int(attrs['id']), Way())
                )
        # For a node in a way
        elif name == 'nd':
            parent = current_state[-1]
            if type(parent) == Way:
                parent.nodes.append(int(attrs['ref']))
            else:
                pass
        # if a tag
        elif name == 'tag':
            parent = current_state[-1]
            if type(parent) in [Node, Way]:
                parent.tags[attrs['k']] = attrs['v']
            else:
                pass
        # For unused relation
        elif name == 'relation':
            current_state.append(None)
        elif name == 'member':
            pass
        else:
            raise ValueError('Unrecognized XML node %s' % name)

    def end_element(name):

        """Call back at the end of elements"""

        if name in ['osm', 'tag', 'member', 'nd']:
            pass
        elif name == 'node':
            new_node = current_state.pop()
            raw_osm.nodes[new_node[0]] = new_node[1]
        elif name == 'way':
            new_way = current_state.pop()
            raw_osm.ways[new_way[0]] = new_way[1]
        elif name == 'relation':
            current_state.pop()
        else:
            raise ValueError('Unrecognized XML node %s' % name)

    parser = expat.ParserCreate()
    parser.StartElementHandler = start_element
    parser.EndElementHandler = end_element
    try:
        input_file = open(file_name, 'r')
        parser.ParseFile(input_file)
    except IOError:
        raise ValueError('Input file %s unable to be opened' % file_name)
    except expat.ExpatError as err:
        raise ValueError(
            'Expat parsing failure at line %d column %d of file %s' % (
                err.lineno, err.offset, input_file
                )
            )

    return raw_osm
