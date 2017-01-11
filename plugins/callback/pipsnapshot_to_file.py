import datetime
import json

class CallbackModule(object):

    def runner_on_ok(self, host, result):
        if 'pipsnapshot' in result:
            filename = "pipsnapshot-{}".format(
                datetime.datetime.utcnow().isoformat()
            )
            with open(filename, 'w') as f:
                f.write(json.dumps(result['pipsnapshot']))
