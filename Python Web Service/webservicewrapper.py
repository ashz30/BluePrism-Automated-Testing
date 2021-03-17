from flask import Flask, jsonify, request

from GenerateTestCoverageRelease import generaterelease
from GetDatabaseSessionData import getDBSessiondata

app = Flask(__name__)

@app.route("/")
def default():
    return "Hello world>>!!"


@app.route('/testcoverage',methods=['GET'])
def testcoverage():
    sessionid = request.args.get('sessionid', None)
    releasepath = request.args.get('releasepath', None)
    newreleasefilename = request.args.get('newreleasefilename', None)
    releasefile = generaterelease(sessionid, releasepath, newreleasefilename)
    return releasefile


@app.route('/getsessiondata',methods=['GET'])
def getsessiondata():
    sessionid = request.args.get('sessionid', None)
    stagename = request.args.get('stagename', None)
    processname = request.args.get('processname', None)
    pagename = request.args.get('pagename', None)
    objectname = request.args.get('objectname', None)
    actionname = request.args.get('actionname', None)

    data = getDBSessiondata(sessionid, stagename, processname, pagename, objectname, actionname)
    return jsonify(data)

if __name__ == "__main__":
    app.run()
