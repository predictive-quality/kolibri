# Copyright (c) 2022 RWTH Aachen - Werkzeugmaschinenlabor (WZL)
# Contact: Simon Cramer, s.cramer@wzl-mq.rwth-aachen.de

shopfloor_config = {
    "name": "SC",
    "description": "Simulation center for the simulated machines."
}
machine_config = {
    "name": "AWK Simulation",
    "description": "Simulation of a CNC machine for the AWK 2021",
    "machinetype": "cnc",
    "shopfloor": None
}
tool_config = {
    "name": "Simulated Milling Head",
    "description": "Milling head of the simulated Machine.",
    "machine": None
}
productspecification_config = {
    "name": "AWK Simulation",
    "description": "Square."
}
pss_cnc_config = {
    "name": "Milling-Simulation",
    "description": "Create square in material.",
    "productspecification": None
}
pss_measurement_config = {
    "name": "Measurement-Simulation",
    "description": "Measure simulated process.",
    "previous_pss": [],
    "productspecification": None
}
