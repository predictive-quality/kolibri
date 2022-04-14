# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import pandas as pd
from absl import logging

from utilities import requestHelper
from .get_config import getConfig
from push_entries_simulation_config import processparameter_ids, sensor_ids
from push_entries_simulation_predictions_config import prediction_sensor_ids


def transport_rest(filepath: str, processStep: str):
    """
    Send all sensorreadings from the file via REST to the server. (VERY SLOW!)

    :param filepath: Filepath to a csv file with the colums id,time,kind,value
    :param processStep: Supported are milling and measurement
    :return: None
    """

    x = pd.read_csv(filepath)
    configCache = {}
    for index, row in x.iterrows():
        product, ps_milling, ps_measurement, ps_prediction ,configCache = getConfig(row['id'], configCache)

        sensorreading_config = {
            "value": row['value'],
            "date": row['time']
        }

        if processStep == "milling":
            sensorreading_config["processstep"] = ps_milling["id"]
            sensorreading_config['processparamter'] = processparameter_ids[row['kind']]
            sensorreading_config["sensor"] = sensor_ids[row['kind']]
        elif processStep == "measurement":
            sensorreading_config["processstep"] = ps_measurement['id']
            sensorreading_config['qualitycharacteristics'] = processparameter_ids[row['kind']]
            sensorreading_config["sensor"] = sensor_ids[row['kind']]
        elif processStep == "prediction":
            sensorreading_config["processstep"] = ps_prediction['id']
            sensorreading_config["sensor"] = prediction_sensor_ids[row['kind']]
        else:
            raise Exception("Processstep unknown {] . Aborting!".format(processStep))


        sensorreading = requestHelper.createOrPatch(['sensorreading'], sensorreading_config)
        #x[index:, :].to_csv(filepath, index=False)
        logging.info("{} processed".format(index))
