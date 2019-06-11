========================
SparkInClimate
========================

SparkInClimate is service for climate data extraction.


Requirement
=================

- Python 3.2
- Docker


Setup project
=================

SparkInClimate is open source project publically available on Bitbucket. To clone the repository, use the following command.

.. code-block:: bash

	git clone https://bitbucket.org/sparkindata-irit/sparkinclimate.git
	cd sparkinclimate
	chmod a+x bin/*



Docker
=================

Sparkinclimate is avaulable as a docker image based on the latest Ubuntu version.
The following command allows to build the docker image *sparkinclimate*.

.. code-block:: bash

	docker build -t sparkinclimate:latest .

In order to run the docker container, be sure that Docker is installed and running then use the next command line.

.. code-block:: bash

	docker run --name=sparkinclimate --restart unless-stopped -d -p 7070:7070 sparkinclimate



Download dataset
==================

Weather newsletters are available for download in PDF format from the web site of Meteo France.
The following command line allows to build a dataset of weather newsletters since 2012.
By default, PDF file are stored in "dataset" directory. This ouput directory can be changed using  "out" option.

.. code-block:: bash

	./bin/dataset --out dataset


Process PDF files
=================

Weather newsletters from Meteo France include a list of important facts, for instance, storms, snow, flooding, etc.  By processing PDF files, weather facts are extracted and represented as a JSON object.
The following command line allows to process the downloaded dataset of newsletters files (see previous section).By default, input PDF files are stored in "dataset" directory. This input directory can be changed using "input" argument.
By default, the output of processed files is redirected to the console. The "--out" argument allow to redirect the output to a text file.  In order to insert facts into ElasticSearch database, the host of ElasticSearch server must be entered using "--elasticsearch” option.


.. code-block:: bash

	./bin/process --input dataset


More information about how weather facts are represented is available on  `sparkinkb <https://bitbucket.org/sparkindata-irit/sparkinkb>`_. project.

REST service
=================

All features for PSF file processing and weather facts extraction are available through  REST service. The following command line allow to run REST server on localhost on port 7070.

.. code-block:: bash

	./bin/start-server --host 127.0.0.1 --port 7070

The following table summarize available methods through the RESTful API server.  All  methods are self-documented using OpenAPI (fka Swagger) specifications, so interactive documentation UI is in place;
More details about the input and the ouput of each method are available on server base URL path, for instance `http://127.0.0.1:7070 <http://127.0.0.1:7070>`_.

+-------------+-------------------------+----------------------------------------------------------------------------+
| HTTP Method | Path                    | Description                                                                |
+=============+=========================+============================================================================+
| GET         | /dates/extract          | Extracts and resolve date and periods from a text based on contextual date |
+-------------+-------------------------+----------------------------------------------------------------------------+
| POST        | /facts/extract          | Extracts weather facts from PDF document of Meteo France weather reports   |
+-------------+-------------------------+----------------------------------------------------------------------------+
| POST        | /pdf/logical            | Transforms PDF document into a logically structured HTML                   |
+-------------+-------------------------+----------------------------------------------------------------------------+
| POST        | /pdf/parse              | Transforms PDF document to HMTL                                            |
+-------------+-------------------------+----------------------------------------------------------------------------+
| GET         | /pdf/template/{id}      | Retrieve the template using its identifier                                 |
+-------------+-------------------------+----------------------------------------------------------------------------+
| GET         | /pdf/templates          | Retrieve the liste of templates                                            |
+-------------+-------------------------+----------------------------------------------------------------------------+
| POST        | /places/annotate        | Extract mentioned places in a text                                         |
+-------------+-------------------------+----------------------------------------------------------------------------+
| GET         | /places/lookup/{name}   | Retrieve a place using its respective name                                 |
+-------------+-------------------------+----------------------------------------------------------------------------+
| GET         | /search/facts           | Searchs weather facts by query, time interval and location                 |
+-------------+-------------------------+----------------------------------------------------------------------------+



Version
===============

SparkInClimate 0.0.1b


Contributors
===============

The following people have contributed to this code:

- Lamjed Ben Jabeur `Lamjed.Ben-Jabeur@irit.fr <mailto:Lamjed.Ben-Jabeur@irit.fr>`_.
  Ba Huy Tran `ba-huy.tran@irit.fr <mailto:ba-huy.tran@irit.fr>`_.

License
===============
This software is governed by the `CeCILL-B license <LICENSE.txt>`_ under French law and abiding by the rules of distribution of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL-B license as circulated by CEA, CNRS and INRIA at the following URL
`http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html <http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html>`_.
