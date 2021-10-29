# credentials: make a file "creds.py" with credentials
from creds import API_KEY # API_KEY = "bearer <KEY>"

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from deta import Deta
from datetime import datetime


app = FastAPI()
deta = Deta()
db = deta.Base("history")




@app.get('/', response_class=HTMLResponse)
def land():
    land = '''
        <p>This experiment will compute the co2e for a given route length and transport weight for different modes of transportation.</p>
    <p>Visit <a href=route?km=1000&weight=10>https://climatiq.alenrozac.com/route?km=1000&weight=10</a></p>
    <p>Change parameters (kilometers, weight in tonnes) directly in the url.</p>
    <p><br><br></p>
    <p>Visit my homepage: <a href="https://www.alenrozac.com">alenrozac.com</a></p> 
    <p>About me: <a href="https://www.alenrozac.com/about">alenrozac.com/about</a></p>
    '''
    return land





@app.get('/route')
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

        # Compare results
        co2e = [resp["co2e"] for resp in response]
        results = list(zip(options, modes, co2e))



    return results



    # print("Response time:", round((time.time()-t)*1000,0), "ms")
    # print("CO2 Equivalent:", resp.json()["co2e"])




