from fragment_analyser import Line, fa_data



def test_regression_line():
    line = Line(fa_data('example_format_unstructured.csv'))
    line.wells
    line.wells[0].df

    well = line.wells[0]
    assert well.get_peak()  == 168

    line.diagnostic()

    peaks = line.get_peaks()
    assert peaks == [168.0, 584.0, 164.0, 1261.0, 168.0, 172.0, 608.0, 164.0,575.0, 583.0, 609.0, None]

    assert line.guess_peak() == 575
    line.set_guess()  # --> guessing
    line.set_guess(600) # -- setting
    assert line.wells[0].guess == 600

    line.get_well_names()

    #line.get_ng_per_ul()

    line = Line(fa_data('example_format_structured.csv'))
    line.diagnostic()


def test_alternate():
    l = Line(fa_data('alternate/peaktable.csv'))
    l.diagnostic()
    assert l.get_peaks()[0:3] == [168,584,164]

    l = Line(fa_data('alternate/peaktable.csv'), lower_bound=1)
    assert l.get_peaks()[0:3] == [65.,65.,164.]
    l.diagnostic()

    l = Line(fa_data('alternate/peaktable.csv'), sigma=50)
    l.set_guess(500)
    assert l.get_peaks()[0:3] == [608., 584., 445.]
    l.diagnostic()

    l = Line(fa_data('alternate/peaktable.csv'), sigma=100)
    l.set_guess(500)
    assert l.get_peaks()[0:3] == [608,584,584]
    l.diagnostic()

    l = Line(fa_data('alternate/peaktable.csv'), sigma=100)
    l.set_guess(1200)
    assert l.get_peaks()[0:3] == [608, 584, 1169]
    l.diagnostic()


def _test_gap():

    l = Line(fa_data('standard_with_flat_cases/peaktable.csv'))
    l.diagnostic()




