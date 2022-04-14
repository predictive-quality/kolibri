# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import json
import uuid as uid

import numpy as np
import pandas as pd
from absl import logging
from wzl import mqtt

from .get_config import getConfig
from push_entries_simulation_config import sensor_ids


def transport_mqtt(filepath: str, processStep: str, mqttPublisher: mqtt.MQTTPublisher, mqtt_topic: str, database: str, chunksize: int = 500):
    """
    Send all sensorreadings from the file via MQTT to the server.

    :param filepath: Filepath to a csv file with the colums id,time,kind,value
    :param processStep: Supported are milling and measurement
    :param mqttPublisher: Connected MQTT publisher object.
    :param mqtt_topic: MQTT topic where sensorreadings can be processed
    :param chunksize: Amount of Sensorreadings to send at once
    :return: None
    """
    x = pd.read_csv(filepath)

    configCache = {}

    index_begin = np.arange(0, x.shape[0], chunksize).tolist()
    index_end = (np.array(index_begin + [x.shape[0]])).tolist()[1:]
    for i in range(len(index_begin)):
        data = []
        subset_x = x.iloc[index_begin[i]:index_end[i], :]

        for uuid in subset_x['id'].unique():
            product, ps_milling, ps_measurement, ps_prediction, configCache = getConfig(uuid, configCache)

            if processStep == "milling":
                ps = ps_milling["id"]
            elif processStep == "measurement":
                ps = ps_measurement['id']
            else:
                raise Exception("Processstep unknown {] . Aborting!".format(processStep))

            for row in subset_x[subset_x['id'] == uuid].iterrows():
                sensor_entry = {"sensor": sensor_ids[row[1]['kind']],
                                "product": product["id"],
                                "processstep": ps,
                                "value": row[1]['value'],
                                "date": row[1]['time']}
                data = data + [sensor_entry]

        message = json.dumps({
            "database": database,
            "data": data
        }
        )
        mqttPublisher.publish(mqtt_topic, message.encode("utf-8"))
        x.iloc[index_end[i]:, :].to_csv(filepath, index=False)
        logging.info("{} processed".format(i))
