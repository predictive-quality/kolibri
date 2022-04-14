# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

from utilities import requestHelper
from push_entries_simulation_config import product_specification_id, processstepspecification_milling_id, \
    processstepspecification_measurement_id, processstepspecification_prediction_id


def getConfig(productUUID: str, configCache: dict={}):
    """
    Get or Create a product, processstep milling, processstep measurement and processstep prediction for a given product UUID.
    To avoid multiple database requests, the configs can be cached in the configCache.
    :param configCache:
    :param productUUID:
    :return:
    """
    if productUUID not in configCache:
        product_specification = {
            "name": productUUID,
            "productspecification": product_specification_id
        }
        product = requestHelper.createOrPatch(['product'], product_specification, checkfor='name')
        ps_milling_config = {
            "name": productUUID + '_milling',
            "status": "Succeeded",
            "processstepspecification": processstepspecification_milling_id,
            "product": product['id']
        }

        ps_milling = requestHelper.createOrPatch(['processstep'], ps_milling_config, checkfor='name')
        ps_measurement_config = {
            "name": productUUID + '_measurement',
            "status": "Succeeded",
            "processstepspecification": processstepspecification_measurement_id,
            "product": product['id']
        }
        ps_measurement = requestHelper.createOrPatch(['processstep'], ps_measurement_config, checkfor='name')

        ps_prediction_config = {
            "name": productUUID + '_prediction',
            "status": "Succeeded",
            "processstepspecification": processstepspecification_prediction_id,
            "product": product['id']
        }

        ps_prediction = requestHelper.createOrPatch(['processstep'], ps_prediction_config, checkfor='name')

        configCache[productUUID] = {
            'product': product,
            'ps_milling': ps_milling,
            'ps_measurement': ps_measurement,
            'ps_prediction': ps_prediction
        }

    return configCache[productUUID]['product'], configCache[productUUID]['ps_milling'], configCache[productUUID][
        'ps_measurement'], configCache[productUUID]['ps_prediction'], configCache
