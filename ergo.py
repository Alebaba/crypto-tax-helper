from datetime import datetime
import json
import time
import requests
import sys
import argparse

parser = argparse.ArgumentParser(description='Get some Ergo transactions.')
parser.add_argument('--address', type=str, default=None)
parser.add_argument('--amount', type=int, default=20) # TODO: replace amount with start and end date
args = parser.parse_args(sys.argv[1:])

# Only 50 Coingecko API calls per minute
def get_price_by_date(date:str) -> float:
    try:
        response = json.loads(requests.get('https://api.coingecko.com/api/v3/coins/ergo/history?date=' 
                                           + date).content.decode())
        price = response['market_data']['current_price']['eur']
        return round(price, 2)
    except Exception as error:
        print(error)
          
# Small transaction amount calls works better. 20 is default
def get_transactions(transaction_offset:int, address:str) -> dict:
    try:
        response = requests.get('https://api.ergoplatform.com/api/v1/addresses/' 
                                + address + '/transactions?limit=20&offset=' 
                                + str(transaction_offset))
        return json.loads(response.content.decode())
    except Exception as error:
        print(error)

if args.address:
    transactions = []
    transaction_offset = 0
    
    while(transaction_offset < args.amount):
        try:
            transactiondata = get_transactions(transaction_offset, args.address)
            for transaction in transactiondata['items']:
                for outputs in transaction['outputs']:
                    if outputs['address'] == args.address and outputs['value'] > 0:
                        timestamp = datetime.utcfromtimestamp(transaction['timestamp']/1000).strftime('%d-%m-%Y')
                        price = get_price_by_date(timestamp)
                        transaction_value = outputs['value']*1e-9 # 'value' is in nanoErgs
                        total_price = price * transaction_value
                        transactions.append(timestamp + ';' 
                                            + str(transaction_value) + ';' 
                                            + str(price) + ';' 
                                            + str(round(total_price, 2)))
                        time.sleep(1.2) # Sleep for 1.2 seconds so the Coingecko API call limit doesn't get exceeded
            transaction_offset = transaction_offset + 20
        except Exception:
            break;
    
    with open('ergotransactions.csv', 'w', encoding='utf-8') as f:
        f.write('SEP=;\n') # Use semicolon as a separator in Excel
        f.write('Date;ERG Amount;ERG Price;Total price €\n\n')
        for transaction in transactions:
            f.write(transaction + '\n')
else:
    print('Please provide Ergo address')

    