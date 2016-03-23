from fragment_analyser.plate import PlatePFGE
import glob
import pandas as pd



def test_plate():
    filenames = glob.glob("test_input*.csv")
    plate = PlatePFGE(filenames)
    plate.output_filename = "test_output.csv"
    plate.to_csv()

    df1 = pd.read_csv("./test_plate.csv")
    df2 = pd.read_csv("./test_output.csv")
    assert all(df1 == df2)

    # todo : remove the test_output.csv file
