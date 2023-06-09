Usage overview
==============

This API answers queries about salmon populations and pre-defined areas of interest to support providing information on how projected climate change may affect salmon populations in the future. It does not provide any climate projections, but provides geometric information that may be used to obtain climate projects from the PCIC Climate Explorer API.

Example Use Case:
-----------------

A user is interested in information about Hope, British Columbia, Canada. Hope is located at latitude 49.385833, longitude -121.441944. The user could query the :doc:`api/region` to find out which of the BC Freshwater Atlas watersheds Hope is in, like so:

::
   
   server/api/region?kind=watershed&overlap=POINT(-121.442%2049.386)

This would return information on the Fraser Canyon watershed, including its boundaries and the most downstream point on the watershed (outlet). The user can query the PCEX `data` API with the boundary of the watershed to see average temperature or precipitation change over the watershed, use the PCEX `streamflow` API to trace the path from this watershed to the sea, or use the PCEW `watershed_streams` API to explore the flow network of this watershed.

To get information on salmon populations in Hope, the user might instead query the :doc:`api/population`:

::
   
   server/api/population?overlap=POINT(-121.442%2049.386)

This would return information on two populations, one Coho, and one Odd Year Pink. If the user only cared about Coho, they could specify that in the query:

::
   
   server/api/population?overlap=POINT(-121.442%2049.386)&common_name=coho

The information returned would include the `boundary` and `outlet` of the salmon population in addition to information about the salmon, so the user could use these geometries to query the PCEX API and explore stream connectivity or projected climate change.

