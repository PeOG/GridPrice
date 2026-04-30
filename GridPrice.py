# -*- coding: utf-8 -*-
import os
import requests
import json
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

def hämta_och_tvätta_priser():
    # Laddar miljövariabler fr?n .env
    load_dotenv()
    api_token = os.getenv('ENTSOE_TOKEN')
    omr?de = "10Y1001A1001A46L" # SE3 EIC-kod
    
    # Här sätter du dina fungerande datum
    start_datum = "202604292200" 
    slut_datum   = "202604302200"

    # Bygger URL:en med de parametrar vi kommit fram till
    url = (f"https://web-api.tp.entsoe.eu/api?securityToken={api_token}"
           f"&documentType=A44&processType=A01"
           f"&in_Domain={omr?de}&out_Domain={omr?de}"
           f"&periodStart={start_datum}&periodEnd={slut_datum}")

    print(f"Hämtar priser för omr?de: {omr?de}")
    
    try:
        svar = requests.get(url)
        if svar.status_code == 200:
            # Hanterar XML-datan och tvättar bort taggarna
            ns = {'ns': 'urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:3'}
            root = ET.fromstring(svar.content)
            
            rensade_priser = []
            
            for punkt in root.findall('.//ns:Point', ns):
                pos = punkt.find('ns:position', ns).text
                pris = punkt.find('ns:price.amount', ns).text
                
                rensade_priser.append({
                    "timme": int(pos),
                    "pris_eur_mwh": float(pris)
                })
            
            # Sparar till den rensade filen
            with open('current_prices_clean.json', 'w') as f:
                json.dump(rensade_priser, f, indent=4)
            
            print(f"Lyckades! {len(rensade_priser)} priser har sparats.")
        else:
            print(f"Kunde inte hämta data. Felkod: {svar.status_code}")
            
    except Exception as e:
        print(f"Ett fel uppstod vid körning: {e}")

if __name__ == "__main__":
    hämta_och_tvätta_priser()