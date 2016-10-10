FragmentAnalyser utilities
===========================

Usage on BIC on central-bio
-----------------------------

Load the module
~~~~~~~~~~~~~~~~

**To do only once**: On central-bio, open a unix shell and if not already done, edit the file .profile (in your home directory) and add this line::

    module use /pasteur/projets/policy01/Matrix/modules

quit the shell (or source the .profile file).


When you open a new terminal, you should now be able to use the fragment_analyser module. You can load it 
in your environment as follows::

    module load fragment_analyser

Issue with the creation of images::

    echo "backend:agg" >> ~/.config/matplotlib/matplotlibrc

Analyse some files
~~~~~~~~~~~~~~~~~~~~

Assuming you want to analyse a set of files starting with '2015' with csv 
extensions, type::

    fragment_analyser --pattern 2015*csv 

If you do not want to create images, add ::

    --no-images

Results are stored in **summary_all.csv** and **summary_filter.csv** files.

There are other options related to the analyse. Please type::

    fragment_analyser --help


Input files must be CSV with the 12 wells. The number of files is not
important.

The tool fragment_analyser will identify the peak across the 12 samples that are
the most relevant. All results will be stored in **summary_all.csv**. If you expect all peaks to be found at the same location, peaks that are outliers should be discarded. In the file **summary_filter.csv** the outliers are to NA (empty string). Once a peak is identified, we keep track of its position (Size in base pair), concentration and a quantity refered to as nM.

Usage::

    fragment_analyser --pattern files*csv 


The file results.csv should contains 4 columns::

    Well,Sample ID,Size (bp),% (Conc.),nmole/L,ng/ul,Avg. Size,RFU,TIC (ng/ul),TIM (nmole/L),Total Conc. (ng/ ul),amount (nM)
    D1,T4,649.0,94.9,11.045,4.3591,716.0,1753.0,4.5912,17.688,4.6007,10.33329382
    D2,T7,610.0,91.9,22.672,8.4052,651.0,4773.0,9.1461,44.465,9.1541,21.19848676
    D3,P1,667.0,92.7,9.132,3.6994,693.0,1999.0,3.989,20.247,4.0108,8.53281052
    D4,Mu,688.0,84.5,3.622,1.5137,678.0,795.0,1.7909,13.168,1.7982,3.384839
    D5,rien,,,,,,,,,,
    D6,rien,,,,,,,,,,
    D7,rien,,,,,,,,,,
    D8,rien,,,,,,,,,,
    D9,rien,990.0,100.0,0.001,0.0006,982.0,20.0,0.0006,0.001,0.0369,0.0009324
    D10,rien,,,,,,,,,,
    D11,rien,,,,,,,,,,
    D12,Ladder,,,,,,,,,,

The 12th well (Ladder) is always empty.

All columns are copies of input files except for the last column that is the concentration in nM unit. and is computed as::

    conc * 1000 / ((Size) * 650 /1000) 
    
where 650 is a hard coded value (mw_dna)


.. image:: diagnostic.png


More help ?
==============

Please see the notebooks directory or the doc directory. The doc directory is a sphinx project and should be compiled for a better rendering. See also the brief but up-to-date documentation using ::

    fragment_analyser --help











