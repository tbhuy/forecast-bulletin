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


Run the following command to build the docker image *sparkinclimate* from web directory

.. code-block:: bash

	docker build -t sparkinclimate:latest .

Run the Docker the container¶

.. code-block:: bash

	docker run -d -p 5000:5000 sparkinclimate

	docker build -t sparkinclimate:latest .
	docker run --name=sparkinclimate --restart unless-stopped -d -p 5000:5000 sparkinclimate
	docker logs -f sparkinclimate


Stop the Docker the container¶

.. code-block:: bash

	docker ps
	docker stop <container_id>


Version
===============

SparkInClimate 0.0.1


Contributors
===============

The following people have contributed to this code:

- Lamjed Ben Jabeur `Lamjed.Ben-Jabeur@irit.fr <mailto:Lamjed.Ben-Jabeur@irit.fr>`_.

License
===============
This software is governed by the `CeCILL-B license <LICENSE.txt>`_ under French law and abiding by the rules of distribution of free software.  You can  use, modify and/ or redistribute the software under the terms of the CeCILL-B license as circulated by CEA, CNRS and INRIA at the following URL
`http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html <http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html>`_.