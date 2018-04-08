# CryptocurrencyPriceTracker
Run python file

python cryptoScript.py

It will insert data into postgres database at intervals of 30 minutes.

For Database :

We have used online elephantsql cloud. Which provides online 20MB database

Link : https://www.elephantsql.com/

Database Connection command

psql postgres://dbuzkqmi:vi24qSFc5TG77k5GPa4aQr3XlnLOBIRf@baasu.db.elephantsql.com:5432/dbuzkqmi( postgres Installation is required)

python notify.py :

It will listen postgres chanel. When any row insert in table it will trigger notification. 
For new inserted data it will check whether it satisfies any alert rules. if it satisfies then system will mail notification to user.
