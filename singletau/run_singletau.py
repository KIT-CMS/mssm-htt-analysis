#!/usr/bin/env python

import argparse
import yaml
import os
import logging

from multiprocessing import Pool
from subprocess import call


logger = logging.getLogger("run_singletau")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def process_file(arguments):
    call(["./singletau/job_singletau.sh {}".format(arguments)], shell=True)


def parse_arguments():
    logger.debug("Parsing arguments.")
    parser = argparse.ArgumentParser(description="test")
    parser.add_argument("--config", required=True, type=str,
                        help="Configuration file.")
    parser.add_argument("--filelist", required=True,
                        help="File list with root files and folders.")
    parser.add_argument("--num-processes", required=True, type=int,
                        help="Number of processes.")
    return parser.parse_args()


def main(args):
    logger.debug("Read filelist and create bash arguments.")
    filelist = yaml.load(open(args.filelist, "r"))
    arguments = []
    for estimation, flist in filelist.iteritems():
        for entry, folders_ in flist.iteritems():
            file_ = entry
            folders = ""
            for folder in folders_:
                folders += "{} ".format(folder)
            folders = folders.strip()
            arguments.append(
                    "{CONFIG} {ESTIMATION} {FILE} {FOLDERS}".
                    format(
                        CONFIG=args.config,
                        ESTIMATION=estimation,
                        FILE=file_,
                        FOLDERS=folders))

    logger.debug("Run jobs with %s processes.", args.num_processes)
    pool = Pool(args.num_processes)
    pool.map(process_file, arguments)
    pool.close()
    pool.join()

    logger.info("Done.")


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
