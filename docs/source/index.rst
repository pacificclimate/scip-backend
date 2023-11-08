.. scip-backend documentation master file, created by
   sphinx-quickstart on Mon Jun  5 16:44:08 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

SCIP backend documentation
========================================

This backend serves data about predefined regions and the locations and details of salmon population to the Salmon Climate Impacts Portal (SCIP).

It accepts parameters either as GET or POST requests. Clients should send GET requests when possible, to facilitate caching and fast return of their queries. However, there are cases where the 'overlap' parameter, a WKT string describing the extent of a region the client wishes information about, is so long it will not fit into a standard 4096 character URL. In those cases, the client may send a POST request with parameters in JSON format in the body.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   api/region
   api/population
   api/taxon



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
