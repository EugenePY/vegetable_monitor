import os
import json

CREDIT = json.loads(os.environ.get("VCAP_SERVICES"))['cloudantNoSQLDB'][0]['credentials']
