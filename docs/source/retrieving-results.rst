
===============
Retrieving data and results
===============

In order to retrieve resources, we need a client instance

.. code-block:: python

  from caplena import Client, resources
  client = Client(api_key="YOUR_API_KEY")



Retrieving projects
~~~~~~~~~~~~~~~

We can retrieve single projects using their ID:

.. code-block:: python

  project = client.projects.retrieve(id="pj_1234k")

Or find mulitple projects using filters:

.. code-block:: python

  from caplena.filters import ProjectsFilter as P

  projects = client.projects.list(filter=P.tags("NPS"))
  for project in projects:
    print(project.id, "-", project.name)


Retrieving Upload status
~~~~~~~~~~~~~~~
Get status of all bulk upload tasks from the last 7 days:

.. code-block:: python

  statuses = client.projects.get_append_status(project_id=project.id)


Get status of one upload task

.. code-block:: python

  status = client.projects.get_append_status(project_id=project.id, task_id="18e5b9c4-3498-45e9-a1ac-77659fdd13e1")



Filtering examples
---------------

Find projects matching multiple tags:

.. code-block:: python

  projects = client.projects.list(filter=P.tags("NPS") & P.tags("test"))

Find projects matching at least one of two tags

.. code-block:: python

  projects = client.projects.list(filter=P.tags("NPS") | P.tags("test"))

Projects created at or after a given date

.. code-block:: python

  client.projects.list(filter=P.created(gte="2022-01-01T00:00:00"))

Projects last modified after given date matching a tag

.. code-block:: python

  client.projects.list(filter=P.last_modified(gte="2022-01-01T00:00:00") & P.tags("NPS"))


Retrieving topics
---------------
Topics discovered and refined in the UI can be retrieved directly from the :code:`ProjectDetail`

.. code-block:: python

  project = client.projects.retrieve(id="pj_1234k")
  for col in project.columns:
      if col.type == 'text_to_analyze':
          print(col.ref, ": ", col.topics)

If the topics array is empty, this means that no analysis has been performed yet.

Retrieving rows
~~~~~~~~~~~~~~~
Rows can be retrieved from the project instance by row id

.. code-block:: python

  row = project.retrieve_row(id="ro_1234k")


or using the client's :code:`ProjectsController`

.. code-block:: python

  row = client.projects.retrieve_row(p_id="pj_werk2", r_id="ro_1ek4d")


Listing rows works similarly to listing projects:

.. code-block:: python

  rows = project.list_rows()
  for row in rows:
    print(row.id)

Filtering rows
---------------

Filters allow you to fetch rows matching specific criteria:

.. code-block:: python

  from caplena.filters import RowsFilter as R
  rows = project.list_rows(filter=R.created(gte="2022-01-01T00:00:00"))

Filter rows for column values. Again, we use the *ref* to reference columns

.. code-block:: python

  rows = project.list_rows(filter=R.Columns.numerical(ref='id', exact=1))

.. code-block:: python

  rows = project.list_rows(filter=R.Columns.text_to_analyze(ref='nps_why', source_language="de"))

Retrieving row values
~~~~~~~~~~~~~~~
Rows are fetched in batches. If we want to have all row values in an object in memory, we
need to iterate through all rows:

.. code-block:: python

  records = []
  rows = project.list_rows()
  for row in rows:
    ref_to_val = {col.ref: col.value for col in row.columns} # mapping from column ref to value
    records.append(ref_to_val)

You can use the :code:`records` to for example populate a database or create a pandas Dataframe

.. code-block:: python

  import pandas as pd
  df = pd.DataFrame(records)


Retrieving analysis results
~~~~~~~~~~~~~~~

Caplena adds results to columns of type :code:`text_to_analyze` during the analysis.
The main results are the :code:`topics` which contain the topics that matches the given :code:`topic.value`.
Each topic has a :code:`topic.label` and a :code:`topic.category` attribute. Topics with :code:`topic.sentiment_enabled=True` also have
the relevant sentiment in :code:`topic.sentiment`.


.. code-block:: python

  rows = project.list_rows()
  for row in rows:
    for col in row.columns:
      if col.type == "text_to_analyze":
        print(f"Results for value: {col.value}")
        print(f"  Overall sentiment: {col.sentiment_overall}")
        print("  Topics: ")
        for topic in col.topics:
          print(f"    Category {topic.category}, Label {topic.label} and Sentiment {topic.sentiment}")
