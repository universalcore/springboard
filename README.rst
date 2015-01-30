Springboard
===========

.. image:: https://travis-ci.org/smn/springboard.svg?branch=develop
    :target: https://travis-ci.org/smn/springboard
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/smn/springboard/badge.png?branch=develop
    :target: https://coveralls.io/r/smn/springboard?branch=develop
    :alt: Code Coverage

.. image:: docs/springboard.gif

Make sure elasticsearch_ is running, then::

    $ git clone https://github.com/smn/springboard.git
    $ cd springboard
    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .
    (ve)$ springboard bootstrap -v
    (ve)$ pserve development.ini --reload


.. _elasticsearch: http://www.elasticsearch.org
