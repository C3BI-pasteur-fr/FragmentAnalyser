from fragment_analyser.plate import Plate
from fragment_analyser import fa_data
import glob
import pandas as pd



def test_plate():

    # unstructured format
    filenames = [fa_data("examples/test_input_well_A.csv"),
        fa_data("examples/test_input_well_B.csv")]


    plate = Plate(filenames)
    plate.analyse()
    plate.filterout()
    print(plate)




    filenames = [fa_data("standard_with_flat_cases/peak_table.csv")]
    plate = Plate(filenames)
    plate.analyse()
    plate.filterout()
    
