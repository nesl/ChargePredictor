import fastavro.reader
from avro import schema
import json
import zlib, cStringIO
from django.conf import settings
def get_schema():
    # TODO: support multiple type
    schema_json = json.loads(
            open(settings.AVRO_SCHEMA_PATH).read()
    )
    type_names = schema.Names()
    array_schema = None
    # TODO: here we assume the LogArray schema is the last one, which night
    # not be the case
    for avro_type in schema_json["types"]:
        array_schema = schema.make_avsc_object(avro_type, type_names)
    return json.loads(str(array_schema))


def parse_binary(avro_binary):
    # decompress it with gzip
    d = zlib.decompress(avro_binary, 16+zlib.MAX_WBITS)

    # make it a buffer
    buf = cStringIO.StringIO(d)

    # load obj with fastavro
    obj = fastavro.reader.read_record(buf, get_schema())

    return obj
