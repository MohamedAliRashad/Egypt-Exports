import warnings

from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from lxml import etree
from pathlib import Path
import json

warnings.filterwarnings("ignore")

import utils

base_path = Path(__file__).parent
dataset_path = (base_path / "dataset").resolve()
dataset_path.mkdir(parents=True, exist_ok=True)

country_codes = [
    "ETH",
    "AZE",
    "ARM",
    "AUS",
    "AFG",
    "ALB",
    "DEU",
    "ATG",
    "AND",
    "IDN",
    "AGO",
    "AIA",
    "URY",
    "UZB",
    "UGA",
    "UKR",
    "IRL",
    "ISL",
    "ERI",
    "ESP",
    "ISR",
    "IOT",
    "IRN",
    "ITA",
    "EST",
    "ARG",
    "JOR",
    "ECU",
    "ARE",
    "BHS",
    "BHR",
    "BRA",
    "PRT",
    "BIH",
    "MNE",
    "DZA",
    "DNK",
    "CPV",
    "SAU",
    "SLV",
    "SEN",
    "SDN",
    "SWE",
    "SOM",
    "CHN",
    "IRQ",
    "GAB",
    "PHL",
    "CMR",
    "COG",
    "KWT",
    "MAR",
    "MEX",
    "GBR",
    "NOR",
    "AUT",
    "NER",
    "IND",
    "USA",
    "JPN",
    "YEM",
    "GRC",
    "PNG",
    "PRY",
    "PAK",
    "BRB",
    "BMU",
    "BRN",
    "BEL",
    "BGR",
    "BLZ",
    "BGD",
    "PAN",
    "BEN",
    "BWA",
    "PRI",
    "BFA",
    "BDI",
    "POL",
    "BOL",
    "PER",
    "THA",
    "TWN",
    "TKM",
    "TUR",
    "TTO",
    "TCD",
    "CHL",
    "TZA",
    "TGO",
    "TUN",
    "TON",
    "JAM",
    "GRL",
    "ANT",
    "VIR",
    "VGB",
    "COM",
    "MDV",
    "UMI",
    "TCA",
    "SLB",
    "FLK",
    "CYM",
    "COK",
    "MHL",
    "CXR",
    "CAF",
    "CZE",
    "DOM",
    "COD",
    "ZAF",
    "GEO",
    "SGS",
    "DJI",
    "DMA",
    "RWA",
    "RUS",
    "ROU",
    "ZMB",
    "ZWE",
    "WSM",
    "ASM",
    "SMR",
    "LCA",
    "SHN",
    "STP",
    "SJM",
    "OMN",
    "SVK",
    "SVN",
    "SGP",
    "SWZ",
    "SYR",
    "SUR",
    "CHE",
    "SLE",
    "LKA",
    "SYC",
    "SRB",
    "TJK",
    "GMB",
    "GHA",
    "GRD",
    "GTM",
    "GLP",
    "GUM",
    "GUY",
    "GUF",
    "GIN",
    "GNQ",
    "GNB",
    "FRA",
    "PSE",
    "VEN",
    "FIN",
    "VNM",
    "FJI",
    "CYP",
    "KGZ",
    "QAT",
    "KAZ",
    "NCL",
    "HRV",
    "KHM",
    "CAN",
    "CUB",
    "CIV",
    "KOR",
    "PRK",
    "CRI",
    "COL",
    "KEN",
    "REU",
    "LVA",
    "LAO",
    "LBN",
    "LUX",
    "LBY",
    "LBR",
    "LTU",
    "LIE",
    "LSO",
    "MTQ",
    "MAC",
    "MLT",
    "MLI",
    "MYS",
    "MYT",
    "MDG",
    "MKD",
    "MWI",
    "MNG",
    "MRT",
    "MUS",
    "MOZ",
    "MDA",
    "MCO",
    "MSR",
    "MMR",
    "NAM",
    "NPL",
    "NGA",
    "NIC",
    "NZL",
    "NIU",
    "HTI",
    "HND",
    "HUN",
    "NLD",
    "HKG",
    "WLF",
]
base_url = "http://www.expoegypt.gov.eg/map/country-info?hscode=0&iso3={country_code}"

for country_code in tqdm(country_codes):
    # Create country folder
    country_path = (dataset_path / country_code).resolve()
    country_path.mkdir(parents=True, exist_ok=True)

    # Get response and parse it
    url = base_url.format(country_code=country_code)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    dom = etree.HTML(str(soup))

    # Get country name
    country_name = dom.xpath("//h3/span/span[@class='text-primary']/text()")[0]

    # Get total exports
    total_export_text = dom.xpath("//div/span[@class='text-primary']/text()")[0]
    total_export_amount, total_export_value = utils.parse_money(total_export_text)

    # Write metadata to metadata.json
    metadata = {"country_name": country_name, "total_export_amount": total_export_amount, "total_export_value": total_export_value}
    with open(country_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    try:
        utils.extract_items_data(dom, country_path / "items.csv")
        utils.extract_yearly_data(dom, country_path / "yearly.csv")
        utils.extract_monthly_yearly_data(dom, country_path / "monthly.csv")
    except Exception as e:
        print(f"Error in {country_code}: {e}")
        print(f"URL: {url}")

utils.clean_dataset(dataset_path)