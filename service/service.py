import datetime
import json

from flask import Flask, Response, request
import os
import logging
from azure.datalake.store import core, lib
from fastavro import writer, reader, parse_schema


app = Flask(__name__)

logger = logging.getLogger('service')

tenant = os.environ["TENANT"]
RESOURCE = os.environ.get("RESOURCE", "https://datalake.azure.net/")
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
avro_schema = parse_schema(json.loads(os.environ["AVRO_SCHEMA"]))

parsed_avro_schema = parse_schema(avro_schema)

store_name = os.environ["STORE_NAME"]

default_perms = os.environ.get("DEFAULT_PERMS", "0777")

adlCreds = lib.auth(tenant_id = tenant,
                    client_secret = client_secret,
                    client_id = client_id,
                    resource = RESOURCE)

adl = core.AzureDLFileSystem(adlCreds, store_name=store_name)


@app.route('/<path:base>', methods=["POST"])
def post(base):
    timestamp = datetime.datetime.now()
    path = os.path.join(base, '{0:%Y/%m/%d/%H/%M/}'.format(timestamp))
    # like mkdir -p
    adl.mkdir(path)
    file = os.path.join(path, '{0:%S.avro}'.format(timestamp))
    if adl.exists(file):
        return Response("File %s already exists\n" % file, status=409)
    with adl.open(file, 'wb') as f:
        logger.info("Writing '%s'", file)
        writer(f, parsed_avro_schema, request.json)
    return Response("Thanks!", mimetype="text/plain")


@app.route('/<path:path>', methods=["GET"])
def get(path):
    def generate():
        with adl.open(path, 'rb') as f:
            logger.info("Reading '%s'", path)
            yield "["
            index=0
            for record in reader(f):
                if index > 0:
                    yield ","
                yield json.dumps(record)
                index = index + 1
            yield "]"
    if not adl.exists(path):
        return Response("Path %s does not exist\n" % path, status=404)
    return Response(generate(), mimetype='application/json', )

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
