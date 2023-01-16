exec &>actual_data_to_guthub.log
echo Started
cp C:/py/tinkoff_trader/PROD/balances.txt C:/git/tinkoff_trader/PROD
cp C:/py/tinkoff_trader/PROD/bought.txt C:/git/tinkoff_trader/PROD
cp C:/py/tinkoff_trader/PROD/sold.txt C:/git/tinkoff_trader/PROD
cd C:/git/tinkoff_trader
git add .
git status
git commit -m "Actual PROD files"
git push https://place-token-here@github.com/MitjaSh/tinkoff_trader.git
echo Finished