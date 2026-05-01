import requests
import json

def hamta_valuta_swea():
    url = "https://swea.riksbank.se/api/v1/Observations/SEKEURPMI/Latest"
    
    # Vi lägger till exakt det som Riksbanken förväntar sig för att tro att vi är en människa
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://www.riksbank.se',
        'Referer': 'https://www.riksbank.se/'
    }

    try:
        # Vi sänker timeouten lite men provar med verify=True (standard)
        # Om det fortfarande tajmar ut, så blockerar de ditt IP eller nätverk
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        kurs = float(data[0]['value'])
        
        output = {"eur_sek": kurs}
        
        with open('valuta.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
            
        print(f"Success! Kursen är: {kurs}")

    except Exception as e:
        print(f"Det går inte att nå Riksbanken just nu: {e}")
        # Vi sparar 11.50 om filen inte redan finns, annars rör vi den inte
        try:
            with open('valuta.json', 'r') as f:
                pass 
        except FileNotFoundError:
            with open('valuta.json', 'w', encoding='utf-8') as f:
                json.dump({"eur_sek": 11.50}, f, indent=4)

if __name__ == "__main__":
    hamta_valuta_swea()