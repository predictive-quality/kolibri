# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import warnings

import pandas as pd
from absl import app
from absl import flags
from absl import logging

from utilities import requestHelper
from create_api_entries_awk_simulation_config import machine_config, pss_cnc_config, pss_measurement_config, \
    productspecification_config, tool_config, shopfloor_config

# Filter warnings, because a bunch of non-checked https Request will be made.
warnings.filterwarnings("ignore")

FLAGS = flags.FLAGS
flags.DEFINE_string("username", None, "Your username for the demonstrator.")
flags.DEFINE_string("password", None, "Your password for the demonstrator")
flags.DEFINE_string("baseurl", "",
                    "Base URL where the Backend can be reached")
flags.DEFINE_string("databasename", "", "Name of the database")
flags.DEFINE_string("apiversion", "v1", "API Version")

# Required flag.
flags.mark_flag_as_required("username")
flags.mark_flag_as_required("password")
flags.DEFINE_string("mqtt_password", "None", "Not used here")


def main(argv):
    # Create RequestHelper singleton
    rH = requestHelper.RequestHelper(username=FLAGS.username,
                                     password=FLAGS.password,
                                     tokenUrl=requestHelper.joinUrl([FLAGS.baseurl, '/users/auth/token/']),
                                     baseUrl=requestHelper.joinUrl(
                                         [FLAGS.baseurl, 'api', FLAGS.apiversion, FLAGS.databasename]))
    rH.getToken()

    # Generate shopflor
    shopfloor = requestHelper.createOrPatch(['shopfloor'], data=shopfloor_config, checkfor='name')
    logging.info('Shopfloor created!')

    # Generate machine
    machine_config["shopfloor"] = shopfloor['id']
    machine = requestHelper.createOrPatch(['machine'], data=machine_config, checkfor='name')
    logging.info('Machine created!')

    # Generate 10 Tools
    tool_config["machine"] = machine['id']
    for i in range(10):
        tool_config["name"] = "Simulated Milling Head " + str(i)
        tool = requestHelper.createOrPatch(['tool'], data=tool_config, checkfor='name')
    logging.info('10 Tools created!')

    # Generate ProductSpecification
    productspecification = requestHelper.createOrPatch(['productspecification'], data=productspecification_config,
                                                       checkfor='name')
    logging.info('ProductSpecification created!')

    # Generate ProcessStepSpecifications
    pss_cnc_config["productspecification"] = productspecification['id']
    pss_cnc = requestHelper.createOrPatch(['processstepspecification'], data=pss_cnc_config, checkfor='name')

    pss_measurement_config["previous_pss"] = [pss_cnc['id']]
    pss_measurement_config["productspecification"] = productspecification['id']
    pss_measurement = requestHelper.createOrPatch(['processstepspecification'], data=pss_measurement_config,
                                                  checkfor='name')

    pss_cnc_config["next_pss"] = [pss_measurement['id']]
    pss_cnc = requestHelper.createOrPatch(['processstepspecification'], data=pss_cnc_config, checkfor='name')

    logging.info('ProcessStepSpecifications generated.')

    # Generate QualityCharacteristics
    qc_df = pd.read_csv('Mapping-QC-Simulation.csv', sep=';')
    qc_df.astype({"SensorName": "str", "SensorID": "int", "description": "str", "targetvalue": "float",
                  "hardupperlimit": "float", "hardlowerlimit": "float", "softupperlimit": "float",
                  "softlowerlimit": "float", "Unit": "str"})

    for index, row in qc_df.iterrows():
        sensor_config = {
            "name": row['SensorName'] + '_Sensor',
            "description": row['description'],
            "virtual": False,
            "machine": machine["id"]
        }

        sensor = requestHelper.createOrPatch(["sensor"], data=sensor_config, checkfor='name')
        qc_df.loc[index, 'SensorID'] = str(int(sensor['id']))

        unit = row['Unit']
        if type(unit) != str:
            unit = ""
        offset_hard = row['targetvalue'] * 0.03
        offset_soft = row['targetvalue'] * 0.015
        qc_config = {
            "name": row['SensorName'],
            "description": "QualityCharacteristic for the sensor " + row['SensorName'],
            "unit": unit,
            "processstepspecification": pss_measurement["id"],
            "sensor": [sensor['id']],
            "targetvalue": row['targetvalue'],
            "hardupperlimit": row['targetvalue'] + offset_hard,
            "hardlowerlimit": row['targetvalue'] - offset_hard,
            "softupperlimit": row['targetvalue'] + offset_soft,
            "softlowerlimit": row['targetvalue'] - offset_soft
        }

        qualityCharacteristic = requestHelper.createOrPatch(["qualitycharacteristics"], data=qc_config,
                                                            checkfor='name')

        logging.info('Sensor {} processed.'.format(row['SensorName']))

    qc_df.to_csv('Mapping-QC-Simulation.csv', sep=';', decimal=',', index=False)
    logging.info('Quality Characteristics generated.')

    # Generate Sensors and ProcessParameter
    sensor_df = pd.read_csv('Mapping-Sensoren-Simulation.csv', sep=';', decimal=',')
    sensor_df.astype({"FunctionName": "str", "SensorName": "str", "SensorID": "str",
                      "Type": "str", "FeedType": "str", "Index": "str", "Axis": "str",
                      "Unit": "str", "Range-min": "float", "Range-max": "float", "Comment": "str"})

    for index, row in sensor_df.iterrows():
        sensor_config = {
            "name": row['SensorName'],
            "description": "",
            "virtual": False,
            "machine": machine["id"],
        }

        sensor = requestHelper.createOrPatch(["sensor"], data=sensor_config, checkfor='name')
        sensor_df.loc[index, 'SensorID'] = str(int(sensor['id']))

        unit = row['Unit']
        if type(unit) != str:
            unit = ""
        processParameter_config = {
            "name": row['SensorName'] + '_PP',
            "description": "ProcessParameter for the sensor " + row['SensorName'],
            "unit": unit,
            "processstepspecification": pss_cnc["id"],
            "sensor": sensor['id']
        }

        processParameter = requestHelper.createOrPatch(["processparameter"], data=processParameter_config,
                                                       checkfor='name')

        logging.info('Sensor {} processed.'.format(row['SensorName']))

    sensor_df.to_csv('Mapping-Sensoren-Simulation.csv', sep=';', decimal=',', index=False)
    logging.info('Sensors generated.')

    logging.info('Program completed!')


if __name__ == '__main__':
    app.run(main)
