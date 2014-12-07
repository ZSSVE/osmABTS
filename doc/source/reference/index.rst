Comprehensive reference manual
==============================

Most of the time, users only need to interact with the instances of the
:py:class:`model.Model` class, defined in the module,

.. autosummary::
    :toctree: generated
    :template: moduletemplate.rst

    osmABTS.model

Under the wrapper, most of the jobs are done by the core functions in the
modules,

.. autosummary::
    :toctree: generated
    :template: moduletemplate.rst

    osmABTS.readosm
    osmABTS.network
    osmABTS.places
    osmABTS.travellers
    osmABTS.trips
    osmABTS.paths

These modules contains functions and classes that is useful for doing non-
straightforward works with this package.
