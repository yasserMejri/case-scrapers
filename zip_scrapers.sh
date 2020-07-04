#!/bin/bash
#grab all the scrapers and base class, and create a zip for deployment to S3
# run this from the root directory

SCRAPER_DIR="./scrapers"
BASE_DIR="./base"
ZIP="/usr/bin/zip"
LAMBDA="./lambdas/scraper.py"
PIPR="./requirements.txt"
LIBRARIES="./libraries"

$ZIP -r scraper $SCRAPER_DIR $BASE_DIR $LAMBDA $PIPR $LIBRARIES
