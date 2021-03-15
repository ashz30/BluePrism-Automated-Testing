import pyodbc
import xml.dom.minidom
import configparser

# only works with trusted connection and below SQL

cp = configparser.ConfigParser()
cp.readfp(open('ConfigFile.properties'))
print(cp['properties']['driver'])
print(cp['properties']['server'])

driver = cp['properties']['driver']
server = cp['properties']['server']
database = cp['properties']['database']
trusted = "yes"
processsessiondatasql = cp['properties']['processsessiondatasql']
objectsessiondatasql = cp['properties']['objectsessiondatasql']
sessiondatasql = cp['properties']['sessiondatasql']




def getDBConn():
    print('starting DB connection')
    connString = "Driver={" + driver + "};Server=" + server + ";Database=" + database + ";Trusted_Connection=" + trusted + ";"
    print("conn String used :" + connString)
    conn = pyodbc.connect(connString)
    print('Connection established')
    return conn


def getRowsFromDB(sessionid, stagename, processname, pagename, objectname, actionname):
    conn = getDBConn()
    print('opening cursor')
    cursor = conn.cursor()
    print('executing select command')
    if processname == 'NULL':
        print('Object SQL used :' + objectsessiondatasql)
        cursor.execute(objectsessiondatasql, sessionid,stagename, objectname, actionname)
    elif objectname == 'NULL':
        print('Process SQL used :' + processsessiondatasql)
        cursor.execute(processsessiondatasql, sessionid, stagename, processname, pagename)
    else :
        print('Both P&O SQL used :' + sessiondatasql)
        cursor.execute(sessiondatasql, sessionid, stagename, processname, pagename, objectname, actionname)
    results = []
    columns = [column[0] for column in cursor.description]
    # print(columns)
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    # print (results)
    conn.close()
    return results

def getinputs(logid, attributexmlDB):
    inputlist = []
    doc = xml.dom.minidom.parseString(attributexmlDB)
    inputelements = doc.getElementsByTagName("input")
    for inputelement in inputelements:
       inputlist.append({"logid" : logid, "sourcetype" : "input","name" : inputelement.getAttribute("name"), "type" : inputelement.getAttribute("type"),"value" : inputelement.getAttribute("value")})
       if inputelement.getAttribute("type") == "collection":
           getcollection(logid, inputlist, inputelement, inputelement.getAttribute("name") + ":collection")
    return inputlist


def getoutputs(logid, attributexmlDB):
    outputlist = []
    doc = xml.dom.minidom.parseString(attributexmlDB)

    outputelements = doc.getElementsByTagName("output")
    for outputelement in outputelements:
        outputlist.append({"logid": logid, "sourcetype": "output", "name": outputelement.getAttribute("name"), "type": outputelement.getAttribute("type"), "value": outputelement.getAttribute("value")})
        if outputelement.getAttribute("type") == "collection":
            getcollection(logid, outputlist, outputelement, outputelement.getAttribute("name") + ":collection")
    return outputlist


def getcollection(logid, elementlist, element, collectionname):

    rows = element.getElementsByTagName("row")
    for row in rows:
        elementlist.append({"logid": logid, "sourcetype": collectionname,"row":"row"})
        fields = row.getElementsByTagName("field")
        for field in fields:
            elementlist.append({"logid": logid, "sourcetype": collectionname, "name": str(field.getAttribute("name") +":"+ collectionname),"type": field.getAttribute("type"), "value": field.getAttribute("value")})
            if field.getAttribute("type") == "collection":
                getcollection(logid, elementlist, field, field.getAttribute("name") + ":collection")


def getDBSessiondata(sessionid, stagename, processname, pagename, objectname, actionname):
    sessiondata = []
    results = getRowsFromDB(sessionid, stagename, processname, pagename, objectname, actionname)
    attributexmlDB = []
    for row in results:
        attributexmlDB.append([str(row['logid']), str(row['attributexml'])])

    for i in range(0, len(attributexmlDB)):
        sessiondata.append(getinputs(attributexmlDB[i][0], attributexmlDB[i][1]))
        sessiondata.append(getoutputs(attributexmlDB[i][0], attributexmlDB[i][1]))

    return sessiondata

def main():

    releasefilelocation = "C:/Users/AEasow/PycharmProjects/TestCoverage/release/Registration Process.bprelease"
    sessionid = 'd7669540-c217-4eef-ad53-2dbd43e2d2fa'
    stagename = 'Submit registration::submit'
    processname = 'Submit Regstration process'
    pagename ='process queue data'
    objectname ='Submit registration'
    actionname = 'submit'
    sessiondata  = getDBSessiondata(sessionid, stagename, processname, pagename, objectname, actionname)
    print(sessiondata)

if __name__ == '__main__':
    main()
