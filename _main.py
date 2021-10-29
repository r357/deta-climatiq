
from fastapi import FastAPI
from scipy.special import comb
from deta import Deta
from datetime import datetime


app = FastAPI()
deta = Deta() #a0ooau3q_Pa5AfdMddu4CahQJ6xJa95LUyWmjdDfN
db = deta.Base("price")


@app.get('/hello')
def hello():
    return "Hello from my Deta Micro"


@app.get('/')
def hi():
    l1 = "Hi! ^_^"
    l2 = "... why are you here?"
    return(l1 + l2)


@app.get('/yes')
def yes():
    from _test import _test
    return(_test())


@app.get('/price')
async def price(exos: int, endoL: int, fc: int, lmax: int):
    from pricing import get_total
    inp = [exos, endoL, fc, lmax]
    vars = ["exoVars", "endoLength", "forecastLength", "l_max",]
    params = dict(zip(vars, inp))
    params["TotalPrice"], params["Tokens"] = get_total(*(inp))
    params["Timestamp"] = str(datetime.now())
    db.put(params) 
    return(params)


@app.get('/priceTest')
def priceTest():
    from pricing import get_total
    if get_total(5, 8*4, 3*4, 3)[0]==16.24: return("Pass") 


# does not work
@app.get('/regTest')
def regTest():
    from scipy import stats
    import numpy as np
    rng = np.random.default_rng()
    x = rng.random(10)
    y = 1.6*x + rng.random(10)
    res = stats.linregress(x, y)
    return(res)