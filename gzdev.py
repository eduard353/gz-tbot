from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from gql_query import *
import csv
import time, datetime
from gql.transport.exceptions import TransportProtocolError
import os
from config import GZ_TOKEN


BASE_URL = 'https://ows.goszakup.gov.kz/v3/graphql'
# HEADERS = {'Authorization': 'Bearer {}'.format(os.environ.get("gz_token")), 'Content-type': 'application/json'}
HEADERS = {'Authorization': 'Bearer {}'.format(GZ_TOKEN), 'Content-type': 'application/json'}
FILE = str(datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")) + '.csv'




async def getLots(name_ru = 'дезин', date_down="2021-12-06", date_up=str(datetime.date.today()), LotStatus=240):
    transport = AIOHTTPTransport(url="https://ows.goszakup.gov.kz/v3/graphql", headers=HEADERS)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    name_ru = '?' + name_ru
    after = 0
    all_result = []
    print('pppppppppppppppppppppppppppppppppppppppppppppppppp')
    while True:
        time.sleep(0.1)
        params = {"nameRu": name_ru, "after": after, "date_down": date_down, "date_up": date_up,
                  'refLotStatusId': LotStatus}
        try:
            result = await client.execute_async(LotsQuery, variable_values=params)
        except TimeoutError:
            print("TimeoutError")
            time.sleep(5)
            continue

        except OSError:
            print("OSError")
            time.sleep(5)
            continue

        except TransportProtocolError:
            print("TransportProtocolError")
            break

        if result["Lots"] is None:
            print("Данные кончались")
            break
        all_result += result["Lots"]

        after = result["Lots"][-1]["id"]
        # print(after)
    print('-'*50)
    # print(all_result)
    lots_dict = {}


    for item in all_result:
        lots_dict[item['id']] = {'lotNumber': item['lotNumber'],'count': item['count'], 'amount': item['amount'], 'nameRu': item['nameRu'],
                                 'descriptionRu': item['descriptionRu'], 'customerNameRu':item['customerNameRu'],
                                 'RefLotsStatus': item['RefLotsStatus']['nameRu'], 'trdBuyId': item['trdBuyId']}
        # print(item['lotNumber'])


    print(' --------------------------------------')
    # print(lots_dict)
    fieldnames = ['lotNumber', 'count', 'amount', 'nameRu', 'descriptionRu', 'customerNameRu', 'RefLotsStatus', 'trdBuyId', 'link']
    if len(lots_dict) >10:
        file_link = 'csv/result' + str(datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")) + '.csv'
        with open(file_link, 'w', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for x, y in lots_dict.items():
                y['link'] = 'https://goszakup.gov.kz/ru/announce/index/{trdBuyId}?tab=lots'.format(trdBuyId=y['trdBuyId'])
                writer.writerow(y)
        return file_link

    else: return lots_dict

async def parseLots(item):
    text = "Номер лота: {lotNumber}\nКоличество: {count}\nСумма: {amount}\nНаименование: {nameRu}\nОписание: {descriptionRu}\nЗаказчик: {customerNameRu}\nСтатус лота: {RefLotsStatus}\nСсылка на объявление: https://goszakup.gov.kz/ru/announce/index/{trdBuyId}?tab=lots".format(lotNumber=item['lotNumber'], count=item['count'], amount=item['amount'], nameRu=item['nameRu'],
                   descriptionRu=item['descriptionRu'], customerNameRu=item['customerNameRu'],
                   RefLotsStatus=item['RefLotsStatus'], trdBuyId=item['trdBuyId'])
    return text

async def getTrds(date_down="2021-01-01", date_up="2021-03-31", name_ru='дезин', sum_min=500000, sum_max=1000000):
    transport = AIOHTTPTransport(url="https://ows.goszakup.gov.kz/v3/graphql", headers=HEADERS)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    name_ru = '?' + name_ru

    after = 0
    stop_signal = 0

    all_result = []

    while stop_signal < 100000000:

        time.sleep(0.0001)
        params = {"nameRu": name_ru, "after": after, "date_down": date_down, "date_up": date_up,
                  "limit_down": sum_min, "limit_up": sum_max}
        try:
            result = await client.execute_async(TrdBuyQuery, variable_values=params)
        except TimeoutError:
            print("TimeoutError")
            time.sleep(5)
            continue

        except OSError:
            print("OSError")
            time.sleep(5)
            continue

        except TransportProtocolError:
            print("TransportProtocolError")
            break

        # save_data(result["TrdBuy"],["id", "totalSum"])
        if result["TrdBuy"] is None:
            print("Данные кончались")
            break

        all_result += result["TrdBuy"]

        after = result["TrdBuy"][-1]["id"]
        print(after)

        stop_signal+=1
        if stop_signal%100 == 0:

            print("Найдено ", stop_signal*10, " строк")
            all_result = []

    print('--------------------------------------')
    print(all_result)

    trdbuy_numbers = []

    for item in all_result:
        print(item['id'])
        trdbuy_numbers.append(item['id'])

    print('first --------------------------------------')
    print(trdbuy_numbers)
    print(len(trdbuy_numbers))

    return trdbuy_numbers
