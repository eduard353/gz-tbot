from gql import gql

ContractQuery = gql(
    """
    query ContractList ($customerBin: String,  $after: Int, $finYear: Int){
        Contract (filter: {customerBin: $customerBin, finYear: $finYear}, limit: 100, after: $after) {

id
contractNumberSys
RefContractYearType
{
    nameRu
}
RefContractStatus
{
    nameRu
}
crdate
contractSum
contractSumWnds
Customer
{
    bin
    nameRu

}
Supplier
{
    bin
    iin
    nameRu

}
FaktTradeMethods
{
    nameRu
}

finYear

descriptionRu

ContractUnits
{
    Plans 
    {
        descRu
        extraDescRu
    }
}


        }
        }
    """
)

SupContractQuery = gql(
    """
    query ContractList ($customerBin: String, $supplierBiin: String,  $after: Int, $finYear: Int){
        Contract (filter: {customerBin: $customerBin, supplierBiin: $supplierBiin, finYear: $finYear}, limit: 100, after: $after) {

id
contractNumberSys
RefContractYearType
{
    nameRu
}
RefContractStatus
{
    nameRu
}
crdate
contractSum
contractSumWnds
Customer
{
    bin
    nameRu

}
Supplier
{
    bin
    iin
    nameRu

}
FaktTradeMethods
{
    nameRu
}

finYear

descriptionRu

ContractUnits
{
    Plans 
    {
        descRu
        extraDescRu
    }
}


        }
        }
    """
)
