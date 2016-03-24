from fragment_analyser import Line, fa_data



def test_line():

    line = Line(fa_data('example_format_unstructured.csv'))
    line.wells
    line.wells[0].df


    well = line.wells[0]
    assert well.get_peak()  == 168


    line.diagnostic()

    peaks = line.get_peaks()
    assert peaks == [168.0, 584.0, 164.0, 1261.0, 168.0, 172.0, 608.0, 164.0, 575.0, 583.0, 609.0]


    assert line.guess_peak() == 575
    line.set_guess()  # --> guessing
    line.set_guess(600) # -- setting
    assert line.wells[0].guess == 600

    line.get_well_names()


    line.get_ng_per_ul()
    


    line = Line(fa_data('example_format_structured.csv'))
    line.diagnostic()
