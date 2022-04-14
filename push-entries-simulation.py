# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import warnings

from absl import app
from absl import flags
from absl import logging
from wzl import mqtt
import uuid

from typing import List

from utilities import requestHelper
from utilities.transport_mqtt import transport_mqtt
# Filter warnings, because a bunch of non-checked https Request will be made.
from utilities.transport_rest import transport_rest

warnings.filterwarnings("ignore")

FLAGS = flags.FLAGS
flags.DEFINE_string("username", None, "Your username for the demonstrator.")
flags.DEFINE_string("password", None, "Your password for the demonstrator")
flags.DEFINE_string("baseurl", "",
                    "Base URL where the Backend can be reached")
flags.DEFINE_string("databasename", "", "Name of the database")
flags.DEFINE_string("apiversion", "v1", "API Version")
flags.DEFINE_string("mqtt_username", "", 'Username for the MQTT Broker')
flags.DEFINE_string("mqtt_password", None, 'Password for the MQTT broker')
flags.DEFINE_string("mqtt_broker", "", 'Host URL of the MQTT Broker')
flags.DEFINE_integer("mqtt_port", 8883, 'Port for the MQTT Broker')
flags.DEFINE_string("mqtt_vhost", "", 'Virtual host of the MQTT Brocker')
flags.DEFINE_string("mqtt_topic_root", "",
                    'MQTT topic to publish to. (Often same as username.)')
flags.DEFINE_string("mqtt_topic_sub", "sensorreadings", 'MQTT subtopic')
flags.DEFINE_string("transport_mode", "mqtt", "Either mqtt or rest. MQTT highly recommeded.")
flags.DEFINE_string("sensors_file", None, "Filepath to the sensorreadings.")
flags.DEFINE_string("qc_file", None, "Filepath to the qualitycharacteristics.")

# Required flag.
flags.mark_flag_as_required("username")
flags.mark_flag_as_required("password")
flags.mark_flag_as_required("sensors_file")
flags.mark_flag_as_required("qc_file")


def main(argv):
    # Create RequestHelper singleton
    rH = requestHelper.RequestHelper(username=FLAGS.username,
                                     password=FLAGS.password,
                                     tokenUrl=requestHelper.joinUrl([FLAGS.baseurl, '/users/auth/token/']),
                                     baseUrl=requestHelper.joinUrl(
                                         [FLAGS.baseurl, 'api', FLAGS.apiversion, FLAGS.databasename]))
    rH.getToken()

    if FLAGS.transport_mode == "rest":
        transport_rest(FLAGS.sensors_file, 'milling')
        transport_rest(FLAGS.qc_file, 'measurement')
    elif FLAGS.transport_mode == "mqtt":

        mqttPublisher = mqtt.MQTTPublisher(username=str(uuid.uuid4()))

        mqttPublisher.connect(broker=FLAGS.mqtt_broker, port=FLAGS.mqtt_port,
                              username=FLAGS.mqtt_vhost + ':' + FLAGS.mqtt_username,
                              password=FLAGS.mqtt_password, ssl=True)
        mqtt_topic = FLAGS.mqtt_topic_root.rstrip('/') + '/' + FLAGS.mqtt_topic_sub

        transport_mqtt(FLAGS.sensors_file, 'milling', mqttPublisher, mqtt_topic, FLAGS.databasename, chunksize=1000)
        transport_mqtt(FLAGS.qc_file, 'measurement', mqttPublisher, mqtt_topic, FLAGS.databasename, chunksize=100)
    else:
        logging.error("Transport mode {} unknown. Aborting!".format(FLAGS.transport_mode))

    logging.info('Program completed!')


if __name__ == '__main__':
    app.run(main)
