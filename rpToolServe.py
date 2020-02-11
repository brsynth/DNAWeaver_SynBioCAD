#!/usr/bin/python

import sys
sys.path.insert(0, '/home/')

import tempfile
import logging

import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api

import rpTool

#######################################################
############## REST ###################################
#######################################################


app = Flask(__name__)
api = Api(app)


def stamp(data, status=1):
    appinfo = {'app': 'DNAWeaver', 'version': '1.0',
               'author': 'Valentin Zulkower, Melchior du Lac',
               'organization': 'Edinburgh Genome Foundry, BRS',
               'time': datetime.now().isoformat(),
               'status': status}
    out = appinfo.copy()
    out['data'] = data
    return out


class RestApp(Resource):
    """ REST App."""
    def post(self):
        return jsonify(stamp(None))
    def get(self):
        return jsonify(stamp(None))


class RestQuery(Resource):
    """ REST interface that generates the Design.
        Avoid returning numpy or pandas object in
        order to keep the client lighter.
    """
    def post(self):
        inputSBOL = request.files['inputSBOL']
        params = json.load(request.files['data'])
        with tempfile.TemporaryDirectory() as tmpOutputFolder:
            inputSBOL.save(tmpOutputFolder+'/input.sbol')
            #with open(tmpOutputFolder+'/input.sbol', 'wb') as insbol:
            #    insbol.write(inputSBOL)
            rpTool.runDNAWeaver(tmpOutputFolder+'/input.sbol',
                                tmpOutputFolder+'/output.xlsx',
                                str(params['method']),
                                params['max_constructs'])
            #######################
            return send_file(open(tmpOutputFolder+'/output.xlsx', 'rb'), as_attachment=True, attachment_filename='DNA_weaver_results.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


#test_input.xml test_output.xlsx any_method
api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    app.run(host="0.0.0.0", port=8888, debug=False, threaded=True)
