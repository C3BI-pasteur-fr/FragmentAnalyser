

#################################
FragmentAnalsyser documentation
#################################

.. contents::

Motivation
============

The `Fragment Analyser platforms <http://aati-us.com/product/fragment-analyzer>`_ are used
as an automated system for the quantification and qualification of NGS libraries, gDNA and RNA.

The following image shows a typical output. The x-axis indicates the size of the
fragment, which is in the range 1-6000. The y-axis indicates the proportion of
such fragment in the entire sample. A CSV file is provided as well with a st of
detected peaks. 

This set of files (image/CSV) is given for 12 wells and may be repeated over
several lines. A posteriori analysis is required and may be tedious.

This package provide tools to read the CSV files and extract the relevant
information into a simplified CSV files and a set of images. 

This prevent users to look manually at the 12 times 8 CSV files.


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

Each Line correspond to an input CSV file and you may provide as many input
files (lines) as you want. Each Line is decomposed into its 12 wells. For each line, a
single peak (the most significant) is detected and reported in a single CSV file
(summary_all.csv). From the command line, type::

    fragment_analyser --pattern *csv

From a Python shell,

.. plot::
    :include-source:

    import fragment_analyser
    filename = fragment_analyser.fa_data("examples/lineB.csv")
    # Each file corresponds to a Line. Here we provide 1 file but you may
    # provide as many as you want
    plate = fragment_analyser.Plate([filename])
    plate.analyse()
    plate.lines[0].diagnostic()
    plate.to_csv("summary.csv")


Input format
===============


See examples in ./share/data or use the function
:func:`~fragment_analyser.fa_data`::

    from fragment_analyser import fa_data
    alternate = fa_data("alternate/peaktable.csv")

See also :class:`~fragment_analyser.peaktable.PeakTableReader`

Output
=============

for each input CSV file, an image is created (see image above). Each red dot in
the image shows the significant peak detected for a well. The data for a well
may contain several peaks (see top image). Usually, one may expect that the same
peak is detected for the same base pair in each well like in this example.
However, this is not always the case; One may mix several type of samples. For
that reason, each detected peak is saved in a CSV file called summary_all.csv

Yet, if the samples are coming from the same sample, one may want to figure out
when the sample was not detected. An additional file called summary_filtered.csv
stored only peaks that were detected at the same/expected position.

The notebooks in ./notebooks directory and the links in the reference section
(here below) give some examples. 




Reference Guide
=================


.. toctree::
    :maxdepth: 2
    :numbered:

    references

