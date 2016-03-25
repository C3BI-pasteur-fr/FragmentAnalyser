from fragment_analyser import Line, fa_data



def test():
    l = Line(fa_data("standard_with_flat_cases/peak_table.csv"))

    l.wells[0].plot()
    l.wells[6].plot()
