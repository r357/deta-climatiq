# credentials: make a file "creds.py" with credentials
from creds import API_KEY # API_KEY = "bearer <KEY>"

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
from deta import Deta
import numpy as np
import requests


app = FastAPI()
deta = Deta()
db = deta.Base("history")




@app.get('/', response_class=HTMLResponse)
def land():
    land = '''
    <p>This experiment will compute CO2 equivalents for a given route length and transport weight for different modes of transportation.</p>
    <p>Visit <a href=route?km=1000&weight=10>https://climatiq.alenrozac.com/route?km=1000&weight=10</a></p>
    <p>Change parameters (kilometers, weight in tonnes) directly in the url.</p>
    <p><br><br></p>
    <p>Visit my homepage: <a href="https://www.alenrozac.com">alenrozac.com</a></p> 
    <p>About me: <a href="https://www.alenrozac.com/about">alenrozac.com/about</a></p>
    '''
    return land





@app.get('/route', response_class=HTMLResponse)
async def route(km: int, weight: int):
    url = "https://beta.api.climatiq.io/estimate"    
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    options = [
        "Air",
        "Road",
        "Rail",
        "Water"
    ]

    modes = [
        "aircraft",
        "medium-and-heavy-duty-truck",
        "rail",
        "waterborne-craft"
    ]

    response = []
    for mode in modes:
        d = str({
            'emission_factor': mode,
            'parameters': {
                'distance': km,
                'weight': weight
            }
        })

        # Make it Climatiq-readable
        _d = d.replace(", ", ",\n") 
        data = _d.replace("'", '"')

        # Get response from Climatiq API
        resp = requests.post(url, headers=headers, data=data)
        if resp.status_code != 200: 
            return "Climatiq-side error"
        else:
            response.append(resp.json())

    # Prepare and store results + meta
    co2e = [resp["co2e"] for resp in response]
    results = list(zip(options, modes, co2e))
    store = (str(datetime.now()), km, weight, results) 
    db.put(list(store)) # f it, just store for now...

    # Compare results
    best = min(co2e)
    besti=np.argmin(co2e)
    compare = [(e/best)-1 for e in co2e]
    comparison = list(zip(options, compare))    
    comparison.remove(comparison[besti])
    
    # Describe results
    h0 = "Input parameters: " + str(km) + " km, " + str(weight) + " tonnes."
    h1 = "Least carbon-intensive mode: <br>" + str(options[besti]) + " at " + str(round(best,2)) + " C02 equivalent."
    h2 = [str(option+" is "+str(round(compare,2))+"x as bad.") for option, compare in comparison]
    h20, h21, h22 = h2

    # Prepare output html
    out = '''
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
    <p>%s</p>
    ''' % (h0, h1, h20, h21, h22)
    return out








