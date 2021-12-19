from gql import gql

query2 = gql(
    """
    query MyQuery($after: Int){
        Subjects (limit: 200, after: $after) {
# Уникальный идентификатор
pid
# БИН
bin
# ИИН
iin
# ИНН
inn
# Наименование на русском языке
nameRu
# Наименование на государственном языке
nameKz
fullName
# Полное наименование на русском языке
fullNameRu
# Полное наименование на государственном языке
fullNameKz
# E-Mail
email
# Телефон
phone
# Web сайт
website
# Флаг Заказчик (1 - да, 0 - Нет)
customer
# Флаг Организатор (1 - да, 0 - Нет)
organizer
# Год регистрации
year
# Флаг резидента
markResident
# Флаг Поставщик (1 - да, 0 - Нет)
supplier
# Тип поставщика (1 - юридическое лицо, 2 - физическое лицо, 3 - ИП)
typeSupplier
# ОКЭД
okedList
# Адреса
Address 
{
address
}
# Сотрудники
Employees
{
iin
resident
fio
disabled
role
roleName
startDate
editDate
endDate
indexDate
}

}


    }
"""
)

LotsQuery = gql(
    """
    query LotsList ($nameRu: String, $after: Int, $date_down: String, $date_up: String, $refLotStatusId: Int){
        Lots (limit: 2, after: $after, filter:{nameRu: $nameRu, lastUpdateDate: [$date_down, $date_up],
         refLotStatusId: [$refLotStatusId]}) {
            id
            lotNumber
            refLotStatusId
            lastUpdateDate
            count
            amount
            nameRu
            descriptionRu
            customerId
            customerBin
            customerNameRu
            trdBuyNumberAnno
            trdBuyId
            refBuyTradeMethodsId
            plnPointKatoList
            RefLotsStatus {
                id
                nameRu
                code
            }
        }
        }
    """
)



RefTradeMethodsQuery = gql(
    """
    query RefTradeMethodsList {
        RefTradeMethods {
            id
            nameRu
            code
            type
            symbolCode
            isActive
            f1
            ord
            f2
        }
        }
    """
)

TrdBuyQuery = gql(
    """
    query TrdBuyList ($nameRu: String, $after: Int, $date_down: String, $date_up: String, $limit_down:Float, $limit_up:Float){
        TrdBuy (filter: {nameRu: $nameRu, publishDate: [$date_down, $date_up], totalSum: [$limit_down, $limit_up]}, limit: 10, after: $after) {

            id
            numberAnno
            nameRu
            totalSum
            countLots
            refTradeMethodsId
            refSubjectTypeId
            customerBin
            customerPid
            customerNameRu
            refBuyStatusId
            startDate
            endDate
            publishDate
            itogiDatePublic
            refTypeTradeId
            idSupplier
            biinSupplier
            parentId
            lastUpdateDate
            finYear
            kato
            systemId
            Lots {
                    id

                }
            RefTradeMethods {
                    id
                }
            RefSubjectType {
                    id
                }
            RefBuyStatus {
                    id
                    nameRu

                }
            RefTypeTrade {
                    id
                }
        }
        }
    """
)
ContractQuery = gql(
    """
    query ContractList ($trdBuyId: [Int],  $after: Int){
        Contract (filter: {trdBuyId: $trdBuyId}, limit: 100, after: $after) {

            id
parentId

rootId

trdBuyId

trdBuyNumberAnno

trdBuyNameRu

trdBuyNameKz

refContractStatusId
deleted

crdate

supplierId

supplierBiin


supplierLegalAddress

signReasonDocName

signReasonDocDate

customerId

customerBin

customerLegalAddress

contractNumberSys

refSubjectTypeId

refSubjectTypesId

finYear

contractSum

contractSumWnds

signDate

ecEndDate


descriptionRu

faktTradeMethodsId


TrdBuy
{
    id
    nameRu
}
Supplier
{
    pid
    nameRu
}

Customer
{
    pid
    nameRu
}

RefContractStatus
{
    id
    nameRu
}

RefContractAgrForm
{
    id
    nameRu
}


RefContractYearType
{
    id
    nameRu
}


FaktTradeMethods
{
    id
    nameRu
}

        }
        }
    """
)

BuyStatusQuery = gql(
    """
    query BuyStatusList  {
         RefCommRoles ( limit: 100) {
     id
     nameRu
     nameKz
     code
     }
    }
    """
)
