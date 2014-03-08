Retweet Analyser
================

Description
-----------

A simple tool to graph the relative retweets achieved by different users
tweeting about a common topic.

Installation
------------

Clone this repository, and install the following onto your machine (exact
package name may differ between distros):

* ``python2.7`` or ``python3``
* ``libpng``
* ``freetype``
* ``pip``

(On Ubuntu, ``libpng`` and ``freetype`` can be installed with ``sudo apt-get
build-dep python-matplotlib``)

Then run::

  pip install -r requirements.txt

Usage
-----

::

   python retweet_analyser.py --keywords keyword1 keyword2 --users user1 user2

Authors
-------

Benjamin Denham (@ben-denham)
