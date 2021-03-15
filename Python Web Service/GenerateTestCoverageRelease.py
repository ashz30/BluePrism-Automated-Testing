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
testcoveragesql = cp['properties']['testcoveragesql']
outputFolderLocation = cp['properties']['outputFolderLocation']



def getDBConn():
    print('starting DB connection')
    connString = "Driver={" + driver + "};Server=" + server + ";Database=" + database + ";Trusted_Connection=" + trusted + ";"
    print("conn String used :" + connString)
    conn = pyodbc.connect(connString)
    print('Connection established')
    return conn


def getRowsFromDB(sessionid):
    conn = getDBConn()
    print('opening cursor')
    cursor = conn.cursor()
    print('executing select command')
    print('SQL used :' + testcoveragesql)
    cursor.execute(testcoveragesql, sessionid)
    results = []
    columns = [column[0] for column in cursor.description]
    # print(columns)
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    # print (results)
    conn.close()
    return results


def readxml(releasefilelocation):
    with open(releasefilelocation, "r") as f:
        xmlstring = f.read()
    # print (xmlstring)
    splitting = xmlstring.split('<', 1)
    # print(splitting[1])
    return "<" + splitting[1]


def updateXML(releaseXml, stagidsDB):
    stagidlist = []
    doc1 = xml.dom.minidom.parseString(releaseXml)
    # remove existing font formatting
    fontnodes = doc1.getElementsByTagName("font")
    for node in fontnodes:
        parent = node.parentNode
        parent.removeChild(node)

    # add new font for stageids covered in testing

    formatelement = doc1.createElement("font")
    formatelement.setAttribute("family", "Segoe UI")
    formatelement.setAttribute("size", "10")
    formatelement.setAttribute("style", "Regular")
    formatelement.setAttribute("color", "339966")

    stages = doc1.getElementsByTagName("stage")

    print("Stageid db: ", stagidsDB)
    for stageidelement in stages:
        stageid = stageidelement.getAttribute("stageid")
        print("stageid" , stageid)

        if stageid in stagidsDB:
            stageidelement.appendChild(formatelement.cloneNode(True))
            print("stageid found " , stageid)
    #print(doc1.toxml())
    return doc1

#function called by web service to generate new formatted release
def generaterelease(sessionid, releasefilelocation, newreleasefilename):
    # get stageids from session log run
    results = getRowsFromDB(sessionid)
    stagidsDB = []
    for row in results:
        stagidsDB.append(str(row['stageid']).lower())

    # read release file
    releasefilexml = readxml(releasefilelocation)
    # add formatting to release file for stageids which have run
    newreleasefile = updateXML(releasefilexml, stagidsDB)

    with open(outputFolderLocation + "/"+ newreleasefilename, "w") as fs:
        fs.write(newreleasefile.toxml())
        fs.close()
    return outputFolderLocation + "/" + newreleasefilename


def main():

    releasefilelocation = "C:/Users/AEasow/PycharmProjects/TestCoverage/release/Registration Process.bprelease"
    sessionid = 'b39881dd-af3f-4efa-a3bb-26fe8e939b35'
    # get stageids from session log run

    results = getRowsFromDB(sessionid)
    stagidsDB = []
    for row in results:
        stagidsDB.append(str(row['stageid']).lower())

    # read release file
    releasefilexml = readxml(releasefilelocation)
    # add formatting to release file for stageids which have run
    newreleasefile = updateXML(releasefilexml, stagidsDB)

    with open(outputFolderLocation + "/testcoverage.bprelease", "w") as fs:
        fs.write(newreleasefile.toxml())
        fs.close()


if __name__ == '__main__':
    main()
