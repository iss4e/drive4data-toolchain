import json
import logging.config
import os
import sys
import warnings

from drive4data.initialization import post_import
from drive4data.initialization import pre_import
from drive4data.initialization.importer import SamplesImporter, SummaryImporter
from iss4e.util import BraceMessage as __
from iss4e.util.config import load_config

__author__ = "Niko Fink"
logger = logging.getLogger(__name__)


def main():
    config = load_config()
    cred = config["drive4data.influx"]

    logger.info(__("Creating output directories in {}", os.getcwd()))
    os.makedirs("tmp", exist_ok=True)
    os.makedirs("out", exist_ok=True)

    root = sys.argv[1]
    logger.info(__("Will load data from {}", root))
    samples = os.path.join(root, "Participants")
    trips = os.path.join(root, "Trip Summaries")
    for dir in [root, samples, trips]:
        if not os.path.isdir(dir):
            raise ValueError("{} is not a directory".format(dir))

    logger.info(__("Analyzing files in {}", samples))
    warnings.filterwarnings('error')
    headers, ids, files_with_3_infos = pre_import.analyze(samples)
    with open("out/headers.json", 'w+') as f:
        json.dump(headers, f, sort_keys=True, indent=4, separators=(',', ': '))
    with open("out/ids.json", 'w+') as f:
        json.dump(ids, f, sort_keys=True, indent=4, separators=(',', ': '))
    with open("out/files_with_3_infos.json", 'w+') as f:
        json.dump(files_with_3_infos, f, sort_keys=True, indent=4, separators=(',', ': '))
    logger.info(__("Analysis results written to {}", os.path.join(os.getcwd(), "out")))

    logger.info(__("Importing data from {}", samples))
    SamplesImporter(cred, "samples").do_import(samples)
    logger.info(__("Importing trip summaries from {}", samples))
    SummaryImporter(cred, "trips_import").do_import(trips)
    logger.info(__("Importing done, analyzing data in DB", samples))

    counts = post_import.analyze(cred)
    with open("out/counts.csv", 'w+') as f:
        post_import.dump(counts, f)
    logger.info(__("Analysis results written to {}", os.path.join(os.getcwd(), "out/counts.csv")))

    logger.info(__("Import complete"))


if __name__ == "__main__":
    main()
