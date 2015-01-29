.. Springboard documentation master file, created by
   sphinx-quickstart on Thu Jan 29 15:33:20 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Springboard's documentation!
=======================================

Springboard is a library and command line tool for scaffolding and
bootstrapping sites for Universal Core.

.. image:: https://travis-ci.org/smn/springboard.svg?branch=develop
    :target: https://travis-ci.org/smn/springboard
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/smn/springboard/badge.png?branch=develop
    :target: https://coveralls.io/r/smn/springboard?branch=develop
    :alt: Code Coverage

.. image:: https://readthedocs.org/projects/springboard/badge/?version=latest
    :target: https://springboard.readthedocs.org
    :alt: Springboard Documentation

Installation
------------

.. code-block:: bash

    pip install springboard

Starting a new site
-------------------

First make sure you have Elasticsearch_ and Redis_ running and then:

.. code-block:: bash

    $ springboard start-app myapp -r https://github.com/universalcore/unicore-cms-content-ffl-tanzania
    $ cd myapp
    $ pip install -e .
    $ springboard bootstrap -v
    $ pserve development.ini --reload

    Starting server in PID 70411.
    serving on http://0.0.0.0:6543

Now visit http://0.0.0.0:6543/ in your browser and see the skeleton site
with the content loaded from the repository.

.. toctree::
   :maxdepth: 2

   tools


.. _Elasticsearch: http://www.elasticsearch.org
.. _Redis: http://www.redis.io


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

