__author__ = 'Lokesh'

import pandas as pd
import MySQLdb
import pandas.io.sql as psql
import dg.settings
from initialize_data import initialize_library
from initialize_lookup_matrix import initialize_lookup

class data_lib():
    Dict = {}

    lookup_matrix = {}

    idElementKey = ''
    idElementValue = -1

    tableDictionary = {}
    whereDictionary = {}
    selectDictionary = {}
    groupbyDictionary = {}
    categoryDictionary = {}
    orderDictionary = {}
    headerDictionary = {}

    # Accepts options i.e. dictionary of dictionary e.g. {'partition':{'partner':'','state',''},'value':{'nScreening':True,'nAdoption':true}}
    # This function is responsible to call function for checking validity of input and functions to make dataframes according to the inputs
    
    def uniqueList(self,ElementsList):
        seen = set()
        seen_add = seen.add
        return [elements for elements in ElementsList if not (elements in seen or seen_add(elements))]

    def handle_controller(self, args, options):

        final_df = pd.DataFrame()

        relevantPartitionDictionary = {}
        relevantValueDictionary = {}

        ilib = initialize_library(options)
        ilookup = initialize_lookup()

        self.tableDictionary = ilib.initializeTableDict()
        self.whereDictionary = ilib.initializeWhereDict()
        self.selectDictionary = ilib.initializeSelectDict()
        self.groupbyDictionary = ilib.initializeGroupByDict()
        self.orderDictionary = ilib.initializeOrderDict()
        self.categoryDictionary = ilib.initializeCategoryDict()
        self.headerDictionary = ilib.initializeHeaderDict()
        self.lookup_matrix = ilookup.read_lookup_csv()

        # --- checking validity of the partition fields and value fields entered by user ---
        if self.check_partitionfield_validity(options['partition']):
            for item in options['partition']:
                if options['partition'][item] != False:
                    relevantPartitionDictionary[item] = options['partition'][item]
        else:
            print "Warning - Invalid input for partition fields"

        if self.check_valuefield_validity(options['value']):

            for item in options['value']:
                if (item == 'list' and options['value']['list'] != False)or(item == 'numVillage' and (options['value']['numVillage']=='numVillageScreening' or options['value']['numVillage']=='numVillageAdoption'))or(item == 'numBlock' and (options['value']['numBlock']=='numBlockScreening' or options['value']['numBlock']=='numBlockAdoption')):

                    relevantValueDictionary[options['value'][item]] = True
                    relevantPartitionDictionary[
                        self.categoryDictionary['partitionCumValues'][options['value'][item]]] = False
                    del relevantPartitionDictionary[self.categoryDictionary['partitionCumValues'][options['value'][item]]]

                if options['value'][item] != False and item != 'list' and (options['value'][item]!='numVillageScreening') and (options['value'][item]!='numVillageAdoption') and (options['value'][item]!='numBlockScreening') and (options['value'][item]!='numBlockAdoption'):#or options['value'][item]!='numBlockScreening'):
                    relevantValueDictionary[item] = options['value'][item]

        else:
            print "Warning - Invalid input for Value fields"

        for input in relevantValueDictionary:
            queryComponents = self.getRequiredTables(relevantPartitionDictionary, input, args, self.lookup_matrix)
#            print "----------------------------------Full SQL Query---------------------------"
            query = self.makeSQLquery(queryComponents[0], queryComponents[1], queryComponents[2], queryComponents[3],
                                      queryComponents[4])
#            print query
#            print "-------------------------------Result--------------------------------"
            df = self.runQuery(query)
            if final_df.empty:
                final_df = df
            else:
                final_df = pd.merge(final_df, df, how='outer')
#                print df
        resultant_df = self.order_data(relevantPartitionDictionary, final_df)
        resultant_df.index += 1
#        print resultant_df
        return resultant_df

    def order_data(self, partitionElements, dataframe):
        header = dataframe.columns.tolist()
        arranged_columns = [None] * len(self.orderDictionary)
        bumper = 0

        for items in partitionElements:
            if partitionElements[items] != False:
                for elements in self.selectDictionary[items]:
                    if self.selectDictionary[items][elements] == True and self.selectDictionary[items].values().count(True) > 1:
                        arranged_columns[len(arranged_columns) + 1] = None
                        arranged_columns[bumper + self.orderDictionary[items]] = self.headerDictionary[items][elements]
                        bumper += 1
                    elif self.selectDictionary[items][elements] == True:
                        arranged_columns[bumper + self.orderDictionary[items]] = self.headerDictionary[items][elements]

        arranged_columns = filter(lambda a: a != None, arranged_columns)
        arranged_columns.append(self.headerDictionary[self.idElementKey][self.groupbyDictionary[self.idElementKey]])
        arranged_columns.extend(list(set(header) - set(arranged_columns)))
        dataframe = dataframe[arranged_columns]
        return dataframe

    # Function to check validity of the partition field inputs by user by comparing with the generalPartitionList
    def check_partitionfield_validity(self, partitionField):
        if set(partitionField.keys()).issubset(self.tableDictionary.keys()):

            return True
        else:
            return False

    # Function to check validity of the value field inputs by user by comparing with the generalValueList
    def check_valuefield_validity(self, valueField):
        if set(valueField.keys()).issubset(self.tableDictionary.keys()):
            return True
        else:
            return False

    def makeSQLquery(self, select_msg, from_msg, where_msg, groupby_msg, orderby_msg):
        query = 'select ' + str(select_msg) + ' from ' + str(from_msg) + ' where ' + str(
            where_msg) + ' group by ' + str(groupby_msg) + ' order by ' + str(orderby_msg)
        return query

    # Function to accept query as a string to execute and make dataframe corresponding to that particular query and return that dataframe
    def runQuery(self, query):
        # Make connection with the database
        mysql_cn = MySQLdb.connect(host='localhost', port=3306, user='root',
                                   passwd=dg.settings.DATABASES['default']['PASSWORD'],
                                   db=dg.settings.DATABASES['default']['NAME'],
                                    charset = 'utf8',
                                     use_unicode = True)
        # Making dataframe
        temp_df = psql.read_sql(query, con=mysql_cn)
        mysql_cn.close()
        return temp_df

    def getRequiredTables(self, partitionDict, valueDictElement, args, lookup_matrix):
        self.Dict.clear()
        selectResult = self.getSelectComponent(partitionDict, valueDictElement)
        fromResult = self.getFromComponent(partitionDict, valueDictElement, lookup_matrix)
        whereResult = self.getWhereComponent(partitionDict, valueDictElement, self.Dict, args, lookup_matrix)
        groupbyResult = self.getGroupByComponent(partitionDict, valueDictElement)

        orderbyResult = self.getOrderByComponent(partitionDict, valueDictElement)
#        print orderbyResult
#        print "----------------------------------SELECT PART------------------------------"
#        print selectResult
#        print "----------------------------------FROM PART--------------------------------"
#        print fromResult
#        print "----------------------------------WHERE PART-------------------------------"
#        print whereResult
#        print "---------------------------------GROUP_BY PART----------------------------"
#        print groupbyResult
#        print "--------------------------------ORDER_BY PART-----------------------------"
#        print orderbyResult
        return (selectResult, fromResult, whereResult, groupbyResult, orderbyResult)

    def getSelectComponent(self, partitionElements, valueElement):
        selectComponentList = []
        selectComponentKeysList = []
        idElementVal = -1
        idElementKey = ''
        if (not partitionElements and 'list' in valueElement) or (not partitionElements and'numVillage' in valueElement) or (not partitionElements and'numBlock' in valueElement):
            idElementVal = self.orderDictionary[self.categoryDictionary['partitionCumValues'][valueElement]]
            idElementKey = self.categoryDictionary['partitionCumValues'][valueElement]
        else:
            for items in partitionElements:
                for i in self.selectDictionary[items]:
                    if (self.selectDictionary[items][i] == True):
                        selectComponentKeysList.append(items)
                        selectComponentList.append(
                            self.tableDictionary[items] + '.' + i + ' AS \'' + self.headerDictionary[items][i] + '\'')
            for items in selectComponentKeysList:
                if self.orderDictionary[items] > idElementVal:
                    idElementVal = self.orderDictionary[items]
                    idElementKey = items

        self.idElementKey = idElementKey
        self.idElementValue = idElementVal
        selectComponentList.append(
            self.tableDictionary[self.idElementKey] + '.' + self.groupbyDictionary[self.idElementKey] + ' AS \'' + self.headerDictionary[self.idElementKey][
                self.groupbyDictionary[self.idElementKey]] + '\'')
        for i in self.selectDictionary[valueElement]:
            if (self.selectDictionary[valueElement][i] == True):
                x = ['count(', 'distinct']
                if all(a in i for a in x):
                    selectComponentList.append(
                        i.replace('count(distinct',
                                  'count(distinct ' + str(self.tableDictionary[valueElement]) + '.') + ' AS \'' +
                        self.headerDictionary[valueElement][i] + '\'')
                elif "count(" in i and "distinct" not in i:
                    selectComponentList.append(
                        i.replace('count(', 'count(' + str(self.tableDictionary[valueElement]) + '.') + ' AS \'' +
                        self.headerDictionary[valueElement][i] + '\'')
                elif "distinct" in i and "count(" not in i:
                    selectComponentList.insert(0, (
                    i.replace('distinct(', ' distinct(' + str(self.tableDictionary[valueElement]) + '.') + ' AS \'' +
                    self.headerDictionary[valueElement][i] + '\''))
                else:
                    selectComponentList.append(
                        str(self.tableDictionary[valueElement]) + '.' + i + ' AS \'' + self.headerDictionary[valueElement][
                            i] + '\'')
        selectComponentList = self.uniqueList(selectComponentList)
        return ','.join(selectComponentList)

    # Function to make tables by recursive calls for tables.
    def makeJoinTable(self, sourceTable, destinationTable, lookup_matrix, occuredTables, Dict):
        if (sourceTable not in occuredTables):
            for i in lookup_matrix[sourceTable][destinationTable]:
                if (i[2] == 'self'):
                    return
                elif (i[2] == 'direct'):
                    if (destinationTable not in occuredTables):
                        occuredTables.append(destinationTable)
                    if (sourceTable in Dict.keys()):
                        if (destinationTable not in Dict[sourceTable]):
                            Dict[sourceTable].append(destinationTable)
                    else:
                        Dict[sourceTable] = [destinationTable]
                    occuredTables.append(sourceTable)
                    return
                else:
                    if (sourceTable in Dict.keys()):
                        Dict[sourceTable].append(i[2])
                    else:
                        Dict[sourceTable] = [i[2]]
                    occuredTables.append(sourceTable)
                    self.makeJoinTable(i[2], destinationTable, lookup_matrix, occuredTables, Dict)
        else:
            return

    # Function to make FROM component of the sql query
    def getFromComponent(self, partitionElements, valueElement, lookup_matrix):
        partitionTables = []
        for i in partitionElements:
            if (i in self.categoryDictionary['geographies']):
                partitionTables.insert(0, self.tableDictionary[i])
            else:
                partitionTables.append(self.tableDictionary[i])
        majorTablesList = []
        tablesOccuredList = []
        counter = 0
        for index, table in enumerate(partitionTables):
            minorTablePath = []
            if table not in self.Dict.keys():
                self.Dict[table] = []
            if (table not in majorTablesList):
                minorTablePath.append(table)
                self.makeJoinTable(table, self.tableDictionary[valueElement], lookup_matrix, tablesOccuredList, self.Dict)
            counter += 1
        majorTablesList = tablesOccuredList

        if not partitionElements:
            if valueElement in self.categoryDictionary['partitionCumValues'].keys():
                majorTablesList.append(self.tableDictionary[valueElement])
        majorTablesList = self.uniqueList(majorTablesList)
        return ' , '.join(majorTablesList)


    # Function to make whereComponent of the query
    def getWhereComponent(self, partitionElements, valueElement, Dictionary, args, lookup_matrix):
        whereString = '1=1'
        whereComponentList = [whereString]
#        print partitionElements

        for items in partitionElements:
            ll=[]
            if partitionElements[items] != True:

#                for elements in partitionElements[items]:
#
                whereComponentList.append(
                self.tableDictionary[items] + '.' + self.whereDictionary[items] + ' in (' + ','.join(str(n) for n in partitionElements[items])+')')

        for i in Dictionary:
            for j in Dictionary[i]:
                for k in range(0, len(lookup_matrix[i][j])):
                    whereComponentList.append(str(i) + '.' + str(lookup_matrix[i][j][k][0]) + '=' + str(j) + '.' + str(
                        lookup_matrix[i][j][k][1]))
        if '.' in str(self.whereDictionary[valueElement]):
            whereComponentList.append(
                str(self.whereDictionary[valueElement]) + ' between \'' + str(args[0]) + '\' and \'' + str(args[1]) + '\'')
        else:
            whereComponentList.append(
                str(self.tableDictionary[valueElement]) + '.' + str(self.whereDictionary[valueElement]) + ' between \'' + str(
                    args[0]) + '\' and \'' + str(args[1]) + '\'')
        return ' and '.join(whereComponentList)

    # Function to make GroupBy component of the sql query
    def getGroupByComponent(self, partitionElements, valueElement):
        groupbyComponentList = ['1']
        for items in partitionElements:
            if partitionElements[items] != False:
                groupbyComponentList.append(self.tableDictionary[items] + '.' + self.groupbyDictionary[items])
        if self.groupbyDictionary[valueElement] != False:
            groupbyComponentList.append(self.tableDictionary[valueElement] + '.' + str(self.groupbyDictionary[valueElement]))
        return ' , '.join(groupbyComponentList)

    # Function to make OrderBy component of the sql query
    def getOrderByComponent(self, partitionElements, valueElements):
        orderbyComponentList = ['1']
        ordered_cols = [None] * len(self.orderDictionary)

        bumper = 0
        for items in partitionElements:
            if partitionElements[items] != False:
                for keys in self.selectDictionary[items]:

                    if self.selectDictionary[items][keys] == True and self.selectDictionary[items].values().count(True) > 1:

                        ordered_cols[len(ordered_cols) + 1] = None
                        ordered_cols[bumper + self.orderDictionary[items]] = '\'' + self.headerDictionary[items][keys] + '\''
                        bumper += 1
                    else:
                        ordered_cols[bumper + self.orderDictionary[items]] = '\'' + self.headerDictionary[items][keys] + '\''
        ordered_cols = filter(lambda a: a != None, ordered_cols)
        orderbyComponentList += ordered_cols
        return ' , '.join(orderbyComponentList)