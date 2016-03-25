

#################################
FragmentAnalsyser documentation
#################################

.. contents::

Motivation
============

Automatic reports/output from fragment analyser data sets.



ADN nano true seq  (small amount) 

.. _example:

.. image:: ../raw_data_example.png


Installation
================


::

    git clone https://github.com/cokelaer/FragmentAnalyser.git
    cd FragmentAnalyser
    python setup.py install 


Usage
=========

::

    fragment_analyser --pattern *csv 


.. plot::

    import fragment_analyser
    line = fragment_analyser.Line("test.csv")
    line.diagnostic()


Input format
===============


See examples in ./share/data or use the function
:func:`~fragment_analyser.fa_data`::

    from fragment_analyser import fa_data
    alternate = fa_data("alternate/peaktable.csv")

See also :class:`~fragment_analyser.peaktable.PeakTableReader`

Output
=============



Reference Guide
=================


.. toctree::
    :maxdepth: 2
    :numbered:

    references

