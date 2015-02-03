Springboard
===========

.. image:: https://travis-ci.org/universalcore/springboard.svg?branch=develop
    :target: https://travis-ci.org/universalcore/springboard
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/universalcore/springboard/badge.png?branch=develop
    :target: https://coveralls.io/r/universalcore/springboard?branch=develop
    :alt: Code Coverage

.. image:: docs/springboard.gif

Make sure elasticsearch_ is running, then::

    $ git clone https://github.com/universalcore/springboard.git
    $ cd springboard
    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .
    (ve)$ springboard bootstrap -v
    (ve)$ pserve development.ini --reload


.. _elasticsearch: http://www.elasticsearch.org
