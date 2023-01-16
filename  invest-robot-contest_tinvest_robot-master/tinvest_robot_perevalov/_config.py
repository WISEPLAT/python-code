import os

_IS_SANDBOX = os.getenv("IS_SANDBOX") == "True"
app_name = os.getenv("TINVEST_APP_NAME") or 'https://github.com/Perevalov/tinvest_robot'
CLASS_CODE_SPB = 'SPBXM'
CLASS_CODE_MSK = 'MOEX'

USD_FIGI = 'BBG0013HGFT4'
FEE = float(os.getenv("TINVEST_FEE") or 0.003)