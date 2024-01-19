
# expected data elements for the analytics model
PREDEFINED_COLUMN_HEADERS = ['customerId', 'customerName', 'contractId', 'contractStartDate', 'contractEndDate', 'totalContractValue']

# supported date formats for the upload files
PREDEFINED_DATE_FORMATS = ['mm/dd/yy', 'dd/mm/yy', 'yyyy/mm/dd']

# corresponding pandas dateformats
PREDEFINED_DATE_FORMAT_MAP = {
    'mm/dd/yy': '%m/%d/%y',
    'dd/mm/yy': '%d/%m/%y',
    'yyyy/mm/dd': '%Y/%m/%d'
}

ARR_DISPLAY_COLUMN_MAP = {
        "lastMonthRevenue" : "Opening Period ARR",
        "newBusiness" : "New Business",
        "upSell" : "Expansion",
        "downSell" : "Contraction",
        "churn" : "Churn",
        "monthlyRevenue" : "Closing Period ARR", 
        "grossRenewalRate" : "Gross Renewal Rate", 
        "netRetentionRate": "Net Retention Rate", 
        "yearlyRevenueGrowth" : "Yearly Revenue Growth Rate",
        "lastMonthRevenueLogo" : "Opening Period Customers",
        "newBusinessLogo" : "New Customers",
        "churnLogo" : "Churned Customer",
        "monthlyRevenueLogo": "Closing Period Customers"

}