# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

#! ALL SENSORS, MACHINES, PROCESSSTEPS- AND PRODUCTSPECIFICATIONS HAVE TO BE IN THE DB ALREADY!

# ID of the product specification which will be imported
product_specification_id = 2
# ID of the processstep milling
processstepspecification_milling_id = 3
# ID of the proccesstep measurement
processstepspecification_measurement_id = 4

processstepspecification_prediction_id = 5

sensor_ids = {
    'x_ist': 211,
    'y_ist': 212,
    'x_soll': 213,
    'y_soll': 214,
    'spindel_voltage': 215,
    'feed_voltage': 216,
    'rot_speed': 217,
    'sp_fwd': 218,
    'QC1': 210,
    'QC2': 225,
    'QC3': 226
}
processparameter_ids = {
    'x_ist': 207,
    'y_ist': 208,
    'x_soll': 209,
    'y_soll': 210,
    'spindel_voltage': 211,
    'feed_voltage': 212,
    'rot_speed': 213,
    'sp_fwd': 214,
    'QC1': 4,
    'QC2': 11,
    'QC3': 12
}
