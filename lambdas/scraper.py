import json
import uuid
import os.path, sys
from multiprocessing import Process, Pipe
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from scrapers import ScraperAZMaricopaSuperior, ScraperAZMaricopaJustice, ScraperCARiversideSuperior, ScraperCASanDiegoSuperior, ScraperCASantaClaraSuperior, ScraperGAFultonSuperior, ScraperMDCourt, ScraperTXTravisSuperior
from base import SUCCESS, INTERNAL_ERROR, NOT_FOUND

QUERY = 'queryStringParameters'
STATUS = 'statusCode'
BASE64_ENCODED = 'isBase64Encoded'
BODY = 'BODY'
STATE = 'state'
COUNTY = 'county'
LAST_NAME = 'lastName'
FIRST_NAME = 'firstName'
DOB = 'dob'
ERROR = 'error'
SITE_ID = 'siteId'
SCRAPER = 'scraper'
RESULT = 'result'

# Provide the list of sites that have scrapers with state and county
class ScrapableSites:
    sites = [
        { STATE: "AZ", COUNTY: "Maricopa", SITE_ID: "az_maricopa", SCRAPER: ScraperAZMaricopaSuperior },
        { STATE: "AZ", COUNTY: "Maricopa", SITE_ID: "az_jmaricopa", SCRAPER: ScraperAZMaricopaJustice },
        { STATE: "CA", COUNTY: "Santa Clara", SITE_ID: "ca_santa_clara", SCRAPER: ScraperCASantaClaraSuperior },
        { STATE: "GA", COUNTY: "Fulton", SITE_ID: "ga_fulton", SCRAPER: ScraperGAFultonSuperior },
        { STATE: "TX", COUNTY: "Travis", SITE_ID: "tx_travis", SCRAPER: ScraperTXTravisSuperior },
        { STATE: "CA", COUNTY: "Riverside", SITE_ID: "ca_riverside", SCRAPER: ScraperCARiversideSuperior },
        { STATE: "CA", COUNTY: "San Diego", SITE_ID: "ca_san_diego", SCRAPER: ScraperCASanDiegoSuperior },
        { STATE: "MD", COUNTY: "", SITE_ID: "maryland", SCRAPER: ScraperMDCourt },
    ]

    # return the scrapable sites with state and county
    def get_sites(self, state, county):
        return_list = []
        for site in self.sites:
            if site[STATE].casefold() == state.casefold() and site[COUNTY].casefold() == county.casefold():
                return_list.append({
                    SITE_ID: site[SITE_ID],   
                    SCRAPER: site[SCRAPER]  # scraper function
                })
        return return_list

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)
#
# Entry point for lambda. Query should look like this:
#
#{
#  'queryStringParameters': {
#    LAST_NAME: "Banks",
#    FIRST_NAME:    "Christina",
#    DOB: "10/22/1978"
#  }
#}
#
# https://<endpoint>?queryStringParameters

def get_scraped_result(event, key, conn):
    sites = ScrapableSites()
    state = event[QUERY][STATE]
    county = event[QUERY][COUNTY]
    data = {}
    results = {}
    sites = sites.get_sites(state, county) # get the scrapable sites with input county/state values
    if len(sites) == 0:
        data =  { STATUS : NOT_FOUND, BASE64_ENCODED: False} # if there is no site, return NOT_FOUND(404) as a response
    else:
        # print(sites)
        for site in sites:
            # print(site)
            response = site[SCRAPER]().scrape(search_parameters = event[QUERY])
            if ERROR in response:
                data = { STATUS : INTERNAL_ERROR, BASE64_ENCODED: False, BODY : response[ERROR] } # if there is any issue during the scraper, return INTERNAL_ERROR(500) with error code
                break
            # print(response[RESULT])
            results[site[SITE_ID]] = response[RESULT]
    if data == {}:
        data = { STATUS : SUCCESS, BASE64_ENCODED: False, BODY : json.dumps(results) }
    
    # print(json.dumps(data, indent=4, cls=DecimalEncoder))
    conn.close()

def lambda_handler (event, context):
    key = str(uuid.uuid1())
    parent_conn, child_conn = Pipe()
    process = Process(target=get_scraped_result, args=(event, key, child_conn,))
    process.start()

    return  { STATUS : SUCCESS, BASE64_ENCODED: False, BODY : json.dumps({'key': key}) }

if __name__ == "__main__":
    event = {
        QUERY: {
            STATE: "AZ",
            COUNTY: "Maricopa",
            LAST_NAME: "Banks",
            FIRST_NAME: "Christina",
            DOB: "10/22/1978"
        }
    }
    
    print(lambda_handler(event, None))
