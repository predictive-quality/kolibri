# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

import warnings

from absl import app
from absl import flags
from absl import logging

from utilities import requestHelper
from utilities.transport_rest import transport_rest

warnings.filterwarnings("ignore")

FLAGS = flags.FLAGS
flags.DEFINE_string("username", None, "Your username for the demonstrator.")
flags.DEFINE_string("password", None, "Your password for the demonstrator")
flags.DEFINE_string("baseurl", "",
                    "Base URL where the Backend can be reached")
flags.DEFINE_string("databasename", "", "Name of the database")
flags.DEFINE_string("apiversion", "v1", "API Version")
flags.DEFINE_string("prediction_file", None, "Filepath to the sensorreadings.")


# Required flag.
flags.mark_flag_as_required("username")
flags.mark_flag_as_required("password")
flags.mark_flag_as_required("prediction_file")



def main(argv):
    # Create RequestHelper singleton
    rH = requestHelper.RequestHelper(username=FLAGS.username,
                                     password=FLAGS.password,
                                     tokenUrl=requestHelper.joinUrl([FLAGS.baseurl, '/users/auth/token/']),
                                     baseUrl=requestHelper.joinUrl(
                                         [FLAGS.baseurl, 'api', FLAGS.apiversion, FLAGS.databasename]))
    rH.getToken()


    transport_rest(filepath=FLAGS.prediction_file, processStep="prediction")

    logging.info('Program completed!')


if __name__ == '__main__':
    app.run(main)
