from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
from trd_query import SupContractQuery
import csv
import datetime
import time
from gql.transport.exceptions import TransportProtocolError
from config import GZ_TOKEN
from asyncio.exceptions import TimeoutError as TiEr


BASE_URL = 'https://ows.goszakup.gov.kz/v3/graphql'
# HEADERS = {'Authorization': 'Bearer {}'.format(os.environ.get("gz_token")), 'Content-type': 'application/json'}
HEADERS = {'Authorization': 'Bearer {}'.format(GZ_TOKEN), 'Content-type': 'application/json'}
FILE = str(datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")) + '.csv'

FIELDS_OF_CSV = ['#', 'Номер договора', 'Тип договора', 'Статус договора', 'Дата создания', 'Сумма договора без НДС',
                 'Сумма договора с НДС', 'БИН Заказчика', 'Наименование Заказчика', 'БИН Поставщика', 'ИИН Поставщика',
                 'Наименование Поставщика', 'Способ закупки', 'Финансовый год', 'Описание договора',
                 'Описание предметов договора']


def create_file(file_name='result.csv'):
    file_link = 'result/' + file_name
    with open(file_link, 'a+', encoding="utf-16") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDS_OF_CSV)
        writer.writeheader()
    return file_link


def read_bins(file='bins.txt'):
    bins_list = []
    with open(file, 'r') as binsfile:
        for line in binsfile:
            print(line[:-1])
            bins_list.append(str(line[:-1]))

    print(bins_list)
    return bins_list


def write_to_file(file_link, data, fieldnames):
    print('Начинаем запись договоров в файл')

    with open(file_link, 'a+', encoding="utf-16") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        for x, y in data.items():
            writer.writerow(y)

    print('Завершена запись договоров в файл')


def proc_contracts(contracts):
    contracts_dict = {}
    contracts_count = len(contracts)
    current_cont_num = 0
    print('Всего договоров в ГО: ', contracts_count)
    for item in contracts:
        current_cont_num += 1

        plans_desc = ''
        trd_desc = ''
        number = 0
        for plan in item['ContractUnits']:
            number += 1

            if item['descriptionRu'] is not None:
                trd_desc = str(item['descriptionRu']).replace('\n', '---').replace('\r', '---')
            else:
                trd_desc = ''

            if plan['Plans'] is not None:
                if plan['Plans']['descRu'] is None:
                    short_desc = ''
                else:
                    short_desc = str(plan['Plans']['descRu']).replace('\n', '---').replace('\r', '---')

                if plan['Plans']['extraDescRu'] is None:
                    full_desc = ''
                else:
                    full_desc = str(plan['Plans']['extraDescRu']).replace('\n', '---').replace('\r', '***')
                plans_desc += str(number) + '. ' + short_desc + '/' + full_desc
            else:
                plans_desc = ''

        supplier = item['Supplier']
        if supplier is not None:
            sup_bin = item['Supplier']['bin']
            sup_iin = item['Supplier']['iin']
            sup_name = item['Supplier']['nameRu']
        else:
            sup_bin = ''
            sup_iin = ''
            sup_name = ''

        trd_method = item['FaktTradeMethods']
        if trd_method is not None:
            trd_mtd = item['FaktTradeMethods']['nameRu']
        else:
            trd_mtd = ''
        contracts_dict[item['id']] = {'#': item['id'], 'Номер договора': item['contractNumberSys'],
                                      'Тип договора': item['RefContractYearType']['nameRu'],
                                      'Статус договора': item['RefContractStatus']['nameRu'],
                                      'Дата создания': item['crdate'],
                                      'Сумма договора без НДС': item['contractSum'],
                                      'Сумма договора с НДС': item['contractSumWnds'],
                                      'БИН Заказчика': item['Customer']['bin'],
                                      'Наименование Заказчика': item['Customer']['nameRu'],
                                      'БИН Поставщика': sup_bin,
                                      'ИИН Поставщика': sup_iin,
                                      'Наименование Поставщика': sup_name,
                                      'Способ закупки': trd_mtd,
                                      'Финансовый год': item['finYear'],
                                      'Описание договора': trd_desc,
                                      'Описание предметов договора': plans_desc}

    print(' --------------------------------------')
    return contracts_dict


def get_contracts(supplier_biin, fin_year=2021, file_link='result/result.csv'):
    transport = AIOHTTPTransport(url="https://ows.goszakup.gov.kz/v3/graphql", headers=HEADERS)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    bin_list = supplier_biin
    bins_count = len(bin_list)
    current_bin_num = 0
    print('Количество ГО: ', bins_count)

    for biin in bin_list:
        after = 0
        all_result = []
        time.sleep(0.3)
        current_bin_num += 1
        print('Начинаем обработку БИН(' + str(current_bin_num) + '/' + str(bins_count) + '): ', biin)
        while True:
            time.sleep(1)
            params = {"customerBin": biin, "after": after, "finYear": fin_year}
            try:
                result = client.execute(SupContractQuery, variable_values=params)

            except TimeoutError:
                print("TimeoutError")
                time.sleep(5)
                continue

            except TiEr:
                print("asyncio TimeoutError")
                time.sleep(5)
                continue

            except OSError:
                print("OSError")
                time.sleep(5)
                continue

            except TransportProtocolError:
                print("TransportProtocolError")
                break

            if result["Contract"] is None:
                print("Данные кончались")
                break

            all_result += result["Contract"]

            after = result["Contract"][-1]["id"]
            time.sleep(0.3)
            print('after: ', after)

        print('Завершена обработка БИН(' + str(current_bin_num) + '/' + str(bins_count) + '): ', biin)
        contracts_dict = proc_contracts(all_result)
        write_to_file(file_link, contracts_dict, FIELDS_OF_CSV)


get_contracts(supplier_biin=read_bins(), file_link=create_file(FILE), fin_year=2020)
