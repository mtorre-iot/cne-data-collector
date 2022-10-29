#
# TTG GLOBAL  - 10/29/2022  
#
import json
import logging
from optparse import OptionParser
import os
import csv
import time
import pandas as pd
from lib.api_classes import CNEResults

from lib.miscfunc import text_to_log_level
#
# Load config file
#
config_dir = 'config/'
config_file = 'config.json'
try:
    with open(os.path.join(config_dir, config_file)) as json_file:
        config = json.load(json_file)
except Exception as e:
    print('Cannot read System configuration file. Program ABORTED. Error: %s', str(e))
    exit()
#
# configure the service logging
#
logging.basicConfig(format=config['log']['format'])
logger = logging.getLogger()
logger.setLevel (text_to_log_level(config['log']['level']))
#
# Read command line parameters
# 
parser = OptionParser()
try:
    parser.add_option ("-v", "--version", dest="version", action="store_true", help=config['opts']['version_help'], default=False)
    parser.add_option ("-s", "--state", dest="current_state", action="store", help=config['opts']['state_help'], default=None)
    parser.add_option ("-o", "--output", dest="output_file", action="store", help=config['opts']['output_file_help'], default=config['opts']['output_file_default'])
    (options, args) = parser.parse_args()
except Exception as e:
    logger.error("Invalid parameters. Try again. Error: " + str(e) + ". Program ABORTED.")
    exit()
#
# Check parameters
#
try:
    current_state = int(options.current_state)
    if (current_state < config['tm']['states']['min']) or (current_state > config['tm']['states']['max']):
        raise Exception()
except Exception as e:
    logger.error("Found invalid state number. Try again. Error: " + str(e) + ". Program ABORTED.")
    exit()

output_file = options.output_file
#
# Read the Tablamesa csv file
#
file_name = config['tm']['file']
try:
    tm_df = pd.read_csv(file_name, encoding=config['tm']['encoding'])
except Exception as e:
    logger.error("There is an error trying to read TM data file: " + str(e) + ". Program ABORTED.")
    exit()
#
# Filter the TM by selected state#
#
try:
    selected_tm = tm_df.loc[tm_df[config['tm']['columns']['cod_estado']] == current_state] 
except Exception as e:
    logger.error("There is an error trying to filter TM data by state: " + str(e) + ". Program ABORTED.")
    exit()
#
# reindex the TM
selected_tm = selected_tm.reset_index()
#
# Now let's try to connect to CNE...
#
web_config = config['web']
electoral_results = CNEResults()
#
# Get some statistics:
logger.info("Total number of mesas: " + str(selected_tm.shape[0]))
#
# Let's go across all centros and mesas
# Open the output file
#
output_lines = []
        
# print headers
line = config['output']['header']

output_lines.append(line)

for index, row in selected_tm.iterrows():
    for i in range(3):
        codigo_centro = int(row[config['tm']['columns']['codigo_centro']])
        mesa = int(row[config['tm']['columns']['mesa']])
        logger.info("Count: " + str(index + 1) + " - collecting data from centro "+ str(codigo_centro) + ", mesa: " + str(mesa)) 
        try:
            electoral_results.Request_results(web_config, codigo_centro, mesa)
        except Exception as e:
            logger.error("There is an error trying gather data from Server. Error: " + str(e) + ". Let's retry...")
            logger.info("retry # " + str(i+1))
            logger.info("Let's wait a while ....t = " + str(config['web']['delay_between_retries']))
            time.sleep(config['web']['delay_between_retries'])
            continue
        #
        # Got the results. 
        # Build the table
        #
        for res in electoral_results.results:
            for party in res.parties:
                line = [electoral_results.est, electoral_results.mun, electoral_results.par, electoral_results.cod, electoral_results.mes, res.name, res.total_votes, party.name, party.votes]
                output_lines.append(line)
        break # break the reries
        #time.sleep(config['web']['delay_between_queries'])
    if (i > 2):
        logger.error("Tried too many times. Program ABORTED")
        exit()

logger.info ("Collection Completed. Total of " + str(len(output_lines)) + " were collected.") 

try:
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        for line in output_lines:
            writer.writerow(line)
except Exception as e:
    logger.error("Error trying to open output file. Try again. Error: " + str(e) + ". Program ABORTED.")
    exit()
logger.info("PROGRAM ENDED.")

