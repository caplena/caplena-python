
===============
Getting Started
===============

Installation
------------

Minimum Version
~~~~~~~~~~~~~~~

We recommend using the latest version of Python. Caplena supports Python 3.8 and newer.

Dependencies
~~~~~~~~~~~~

The following distributions will be installed automatically when installing Caplena.

* `Requests <https://docs.python-requests.org/en/latest/>`_ is an elegant and simple HTTP library for Python.
* `Typing Extensions <https://github.com/python/typing/tree/master/typing_extensions>`_ enables use of new type system features on older Python versions.

Installing Caplena
~~~~~~~~~~~~~~~~~~

Within your Python environment of choice, use the following command to install Caplena:

.. code-block:: sh

  $ pip install caplena

Caplena is now installed. Continue reading to learn how you can send your very first
API request to Caplena.

Your First API Request
----------------------

Let us now check that everything is working as intended. For this, we will create a small
script that lists the total number of English or German projects in your account along with the names for
the first 10 projects.

Create a new file :code:`main.py` and import the Caplena client in your application code:

.. code-block:: python

  from caplena import Client

Next, you'll want to create a new client, replacing :code:`YOUR_API_KEY` with your account's
API key. If you don't know your key, head over to our `app <https://caplena.com/app/account?tab=api`
and generate a new one.

.. code-block:: python

  client = Client(api_key="YOUR_API_KEY")

Now, before making our first API request, we will want to build a filter such that we only receive
English or German projects. To do so, we will first import our :code:`ProjectsFilter` and then build our
filter accordingly.

.. code-block:: python

  from caplena.filters import ProjectsFilter as P

  language_filter = P.language('en') | P.language('de')

We're now finally ready to retrieve 10 projects matching the :code:`language_filter` from your account.
We can retrieve and iterate over those results as follows:

.. code-block:: python

  projects = client.projects.list(filter=language_filter)

  print('No. of German or English projects:', projects.count)
  for project in projects:
    print("- ", project.name)

Now, let's execute the code by running :code:`python main.py`. If the script lists a few of your account's
projects, you are all set and can now start integrating the library into your own projects.
