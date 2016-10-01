from fragment_analyser import fa_data



def test_fa():
    fa_data("alternate/peaktable.csv")
    try:
        fa_data("dummy.csv")
        assert False
    except:
        assert True
