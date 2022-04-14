# kolibri

### Prepare your environment:

```shell
pip install -r requirements.txt
pip install s3-smart-open --extra-index-url https://git-package-read-token:hiZnxRXN2S1b-BsEavXJ@git-ce.rwth-aachen.de/api/v4/projects/4473/packages/pypi/simple
```


## Create Api Entries Simulation/AWK

In the file `Mapping-QC-Simulation.csv` all Quality Parameters for the simulated AWK part are listed, along with their
specification. In the file `Mapping-Sensoren-Simulation.csv` all sensors of the simulated machine are listed, along with the
specifications for the process parameters for the simulated AWK part. The script will update the column `SensorID` with the
response from the database. It further checks if a sensor/process parameter/quality characteristic with the same name
already exists to avoid duplicate entries.

```shell
python create-api-entries-awk-product.py --flagfile example/api-entries.txt
```

### Options and default values
All options can be passed as command line arguments or in the flagfile

| FLAG | Default | Description |
| --- | --- | --- |
| username |  | Your username for the demonstrator |
| password |  | Your password for the demonstrator |
| baseurl |  | Base URL where the Backend can be reached |
| databasename | default | Name of the database |
| apiversion | v1 | API Version |

## Push Entries from AWK Simulation

This script adds products, process steps and sensorreadings of the AWK simulation to the database via either MQTT or the REST interface.
The process is:

1. Run simulation as described
   in [CNC-Simulation](LINK).
2. Make sure that DB entries for sensor etc. are correct. (See push_entries_config.py)
4. Set the correct paths to input/output file and add passwords to flagfile.
3. `python push-entries-simulation.py --flagfile examples/push-simulation.txt`

### Options and default values
All options can be passed as command line arguments or in the flagfile

| FLAG | Default | Description |
| --- | --- | --- |
| username |   | Your username for the demonstrator. |
| password |   | Your password for the demonstrator. |
| baseurl |   | "Base URL where the Backend can be reached |
| databasename | default | Name of the database |
| apiversion | v1 | API Version |
| mqtt_username |   | Username for the MQTT Broker |
| mqtt_password |   | Password for the MQTT broker |
| mqtt_broker |   | Host URL of the MQTT Broker |
| mqtt_port | 8883 | Port for the MQTT Broker |
| mqtt_vhost |   | Virtual host of the MQTT Brocker |
| mqtt_topic_root |   | MQTT topic to publish to. (Often same as username.) |
| mqtt_topic_sub | sensorreadings | MQTT subtopic |
| transport_mode | mqtt | Either mqtt or rest. MQTT highly recommeded. |
| sensors_file |  | Filepath to the sensorreadings. |
| qc_file |  | Filepath to the qualitycharacteristics. |
