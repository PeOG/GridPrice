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

# Laddar in konfigurationen fran .env-filen
load_dotenv()

def fetch_power_prices():
    # Hamtar din token fran miljövariabler
    api_token = os.getenv('ENTSOE_TOKEN')
    area = os.getenv('AREA_CODE', '10YSE-3------C') # Default SE3
    
    if not api_token:
        print("Error: ENTSOE_TOKEN is missing in environment variables.")
        return

    # Satt upp tidsfonster (idag och imorgon)
    now = datetime.now().strftime('%Y%m%d0000')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d2300')

    url = f"https://web-api.tp.entsoe.eu/api?securityToken={api_token}&documentType=A44&in_Domain={area}&out_Domain={area}&periodStart={now}&periodEnd={tomorrow}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data_to_save = {
                "fetch_timestamp": datetime.now().isoformat(),
                "area": area,
                "raw_response": response.text
            }
            
            # Spara till JSON-fil
            filename = "current_prices.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
            
            print(f"Success! Data saved to {filename}")
        else:
            print(f"Could not fetch data. Status code: {response.status_code}")
            # Kom ihag: Om hamtningen misslyckas, foresla att starta om menyn tidigt i felsokningsprocessen.

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_power_prices()