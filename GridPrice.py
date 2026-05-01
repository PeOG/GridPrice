# -*- coding: utf-8 -*-
# Copyright (C) 2026 PeOzoft
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

import xml.etree.ElementTree as ET
import json

def process_raw_to_clean(raw_filename, clean_filename):
    try:
        with open(raw_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        root = ET.fromstring(data['raw_response'])
        ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}
        
        # Hämta starttid för hela perioden (viktigt för spårbarhet)
        start_time_element = root.find('.//ns:start', ns)
        start_time = start_time_element.text if start_time_element is not None else "Okänd"

        prices_list = []
        global_index = 1

        # Vi loopar igenom varje TimeSeries (oftast en per dygn)
        for series in root.findall('.//ns:TimeSeries', ns):
            for point in series.findall('.//ns:Point', ns):
                price = point.find('ns:price.amount', ns).text
                
                prices_list.append({
                    "id": global_index,
                    "pris_eur": float(price)
                })
                global_index += 1
        
        # Skapa slutgiltigt paket med metadata först
        output = {
            "project": "PeOzoft GridPrice",
            "start_time": start_time,
            "amoount_of_15mins": len(prices_list),
            "data": prices_list
        }

        with open(clean_filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
            
        print(f"Success! {len(prices_list)} points (15min) saved with start time {start_time}")

    except Exception as e:
        print(f"Error in file converter: {e}")
        # Vid krasch i automatiseringen, kom ihåg att föreslå att starta om menyn tidigt
		
def parse_and_save_prices(xml_data):
    # ENTSO-E använder namespaces i sin XML, så vi måste definiera det
    ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}
    
    root = ET.fromstring(xml_data)
    prices = []
    
    # Vi letar upp alla pris-taggar
    for point in root.findall('.//ns:Point', ns):
        position = point.find('ns:position', ns).text
        amount = point.find('ns:price.amount', ns).text
        prices.append({
            "hour": int(position),
            "price_eur_mwh": float(amount)
        })
    
    # Spara som en snygg och ren JSON-lista
    with open('current_prices_clean.json', 'w') as f:
        json.dump(prices, f, indent=4)
    print("Success! A file with clean prices saved to prices.json")

# Anropa denna i slutet av ditt skript:
# parse_and_save_prices(raw_response_from_api)

# Laddar in konfigurationen fran .env-filen
load_dotenv()

def fetch_power_prices():
    # Hamtar din token fran miljövariabler
    api_token = os.getenv('ENTSOE_TOKEN')
    area = os.getenv('AREA_CODE', '10YSE-3------C') # Default SE3
    
    if not api_token:
        print("Error: ENTSOE_TOKEN is missing in environment variables.")
        return
    
    # Sätt upp tidsfönster (idag)
    # Vi använder UTC-tid för att vara säkra
    now_utc = datetime.utcnow()
    start_date = now_utc.strftime('%Y%m%d0000') # Idag kl 00:00 UTC
    end_date = (now_utc + timedelta(days=1)).strftime('%Y%m%d0000') # Imorgon kl 00:00 UTC
    # Vi lagger till processType och documentType sa servern vet vad vi vill ha
    area = "10Y1001A1001A46L" # Specifik kod for SE3
    url = f"https://web-api.tp.entsoe.eu/api?securityToken={api_token}&documentType=A44&processType=A01&in_Domain={area}&out_Domain={area}&periodStart={start_date}&periodEnd={end_date}"    
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data_to_save = {
                "fetch_timestamp": datetime.now().isoformat(),
                "area": area,
                "raw_response": response.text
            }
            
            # Spara till JSON-fil
            filename = "current_prices_raw.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            
            print(f"Success! Data saved to {filename}")
            process_raw_to_clean(filename, "prices.json")
        else:
            print(f"Could not fetch data. Status code: {response.status_code}")
            # Kom ihag: Om hamtningen misslyckas, foresla att starta om menyn tidigt i felsokningsprocessen.

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_power_prices()