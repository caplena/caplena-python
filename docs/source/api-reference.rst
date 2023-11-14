
=============
API Reference
=============

.. module:: caplena

This part of the documentation covers all the interfaces of our client library.


Client
------

.. autoclass:: Client
    :members:
    :inherited-members:


Controllers
-----------

.. autoclass:: caplena.controllers.ProjectsController
    :members:


Resources
---------

.. autoclass:: caplena.resources.ProjectDetail
    :members:

.. autoclass:: caplena.resources.ListedProject
    :members:

.. autoclass:: caplena.resources.RowsAppend
    :members:

.. autoclass:: caplena.resources.RowsAppendStatus
    :members:

.. autoclass:: caplena.resources.Row
    :members:


Filters
-------

.. autoclass:: caplena.filters.ProjectsFilter
    :members:
    :inherited-members:
    :special-members: __and__, __or__

.. autoclass:: caplena.filters.RowsFilter
    :members:
    :inherited-members:
    :special-members: __and__, __or__


Iterator
--------

.. autoclass:: caplena.iterator.CaplenaIterator
    :members:

Exceptions
----------

.. autoclass:: caplena.api.ApiException
    :members:
