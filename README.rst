Retweet Analysis
================

Description
-----------

Simple tool to graph the relative retweets achieved by different users tweeting
about a common topic.

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
   python retweet_analysis.py "#keyword" "user1", "user2"
