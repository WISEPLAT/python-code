from tinvest_robot_perevalov._config import CLASS_CODE_SPB, USD_FIGI, CLASS_CODE_MSK


def test_constants():
    assert CLASS_CODE_SPB == 'SPBXM'
    assert CLASS_CODE_MSK == 'MOEX'
    assert USD_FIGI == 'BBG0013HGFT4'