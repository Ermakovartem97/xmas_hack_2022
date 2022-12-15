import datetime
import requests
import apimoex
import pandas as pd

start = datetime.datetime.now()

# Set the URL for the MOEX API endpoint
url = "https://iss.moex.com/iss/engines/stock/markets/shares/securities.json"

# Set the parameters for the API request
params = {
    "iss.only": "securities",
    "securities.columns": "SECID",
    "securities.market": "shares"
}

# Send the API request and store the response
response = requests.get(url, params=params)

# Print the list of stock names
all_securities = []
for security in response.json()["securities"]["data"]:
    all_securities.append(security[0])

print(all_securities)
date_start = '2022-10-01'

status = 0

with requests.Session() as session:
    for securities in all_securities:
        data = apimoex.get_board_history(session, securities, start=date_start)
        if data:
            df = pd.DataFrame(data)
            df.insert(loc=0, column="NAME", value=securities)
            if status == 0:
                all_df = df
                status = 1
            else:
                all_df = pd.concat([all_df,df])
        #df.set_index('TRADEDATE', inplace=True)

print(all_df.reset_index(drop=True))
print(datetime.datetime.now() - start)

