
===============
Creating Projects and adding rows
===============

Creating the project
~~~~~~~~~~~~~~~
In order to create a project, we need a client instance

.. code-block:: python

  from caplena import Client, resources
  client = Client(api_key="YOUR_API_KEY")


Next, we'll build the project's columns which defines the schema of the rows to be added.

.. code-block:: python

  columns = [
    {
        "name": "Survey Response ID", # name is what is shown in the User Interface
        "ref": "id", # ref is a unique identifier for the column in the project
        "type": "numerical"
    },
    {
        "name": "Why did you give this rating?",
        "ref": "nps_why",
        "type": "text_to_analyze",
        "description": "Please explain the rating in a few sentences."
    }
  ]

Now we're ready to create the project:

.. code-block:: python

  new_project = client.projects.create(name="NPS Study", language='en', columns=columns, tags=["NPS"])

Optionally, we can pass :code:`translation_engine=google_translate` to translate rows automatically using Google Translate.

The newly created `new_project` has a generated unique identifier :code:`new_project.id`. The schema can be inspected using
:code:`new_project.columns`.


Appending rows
~~~~~~~~~~~~~~~

We can now proceed to add rows to the project. We can add a maximum of 20 rows per request, so we need to batch our data:

In this example, we'll generate some fake rows. For your application you may for example read from your database, another API or a CSV.
The ordering of columns within a row does not matter as columns are referenced using the *ref*

.. code-block:: python

  # generate fake rows
  rows = [
    {"columns": [{"ref": "id", "value": i}, {"ref":"nps_why", "value": f"Row {i}"}]}
     for i in range(100)
  ]
  # batch rows, we'll use numpy for this
  import numpy as np
  n_batches = np.ceil(len(rows)/20) # compute the number of batches needed
  row_batches = np.array_split(rows, n_batches) # do the batching

  new_rows = []
  for row_batch in row_batches:
      new_rows.append(new_project.append_rows(rows=list(row_batch))) # need to cast to list from ndarray


This process takes a while, to monitor the status you can use `task_id` property from the `RowsAppend` response and call `get_append_status`.

.. code-block:: python

  # Check append status one by one using their IDs:
  for append_task in new_rows:
      while new_project.get_append_status(task_id=append_task.task_id).status == 'in_progress':
          time.sleep(10)
  # OR
  # Check all append statuses form the project
  all_tasks = new_project.get_append_status()
  for task in all_tasks.tasks:
      if task['status'] == 'in_progress':
          # Do something when upload not ready
      elif task['status'] == 'failed':
          # Do something when task has failed
      elif task['status'] == 'timed_out':
          # Do something when task timed_out
      elif task['status'] == 'succeeded':
          # Do something when task succeeded

When all upload tasks will succeeded the data will be uploaded to Caplena and ready to be analyzed!
