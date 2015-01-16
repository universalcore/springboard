Springboard
===========

Make sure elasticsearch_ is running, then::

    $ git clone https://github.com/smn/springboard.git
    $ cd springboard
    $ virtualenv ve
    $ source ve/bin/activate
    (ve)$ pip install -e .
    (ve)$ springboard bootstrap -v
    (ve)$ pserve development.ini --reload


.. _elasticsearch: http://www.elasticsearch.org
