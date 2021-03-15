from flask import Flask, jsonify, request

from GenerateTestCoverageRelease import generaterelease
from GetDatabaseSessionData import getDBSessiondata

app = Flask(__name__)

@app.route("/")
def default():
    return "Hello world>>!!"

@app.route('/testcoverage/<sessionid>,<path:subpath>,<newreleasefilename>',methods=['GET'])
def structure(sessionid, subpath, newreleasefilename):
    releasefile = generaterelease(sessionid, subpath, newreleasefilename)
    return releasefile


@app.route('/getsessiondata/<sessionid>,<stagename>,<processname>,<pagename>,<objectname>,<actionname>',methods=['GET'])
def getsessiondata(sessionid, stagename, processname, pagename, objectname, actionname):
    data = getDBSessiondata(sessionid, stagename, processname, pagename, objectname, actionname)
    return jsonify(data)


if __name__ == "__main__":
    app.run()
