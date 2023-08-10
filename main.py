from fastapi import FastAPI
from pydantic import BaseModel

from pytapi import PyTAPI
from xmlgenerator import XMLGenerator


class PhoneRawData(BaseModel):
    data: str


class PhoneTextData(BaseModel):
    title: str
    prompt: str
    text: str


class PhoneRingData(BaseModel):
    tone: str


class PhonePrepareCallData(BaseModel):
    targetname: str
    targetdn: str


app = FastAPI()
pytapi = None


@app.on_event("startup")
async def startup_event():
    global pytapi
    pytapi = PyTAPI()


@app.on_event("shutdown")
async def shutdown_event():
    global pytapi
    pytapi.clean()
    del pytapi


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/phone/{name}/raw/")
async def create_item(name: str, phone: PhoneRawData):
    global pytapi
    pytapi.sendDataBySEP(name, str(phone.data).strip())
    return phone


@app.post("/phone/{name}/text/")
async def create_item(name: str, phone: PhoneTextData):
    global pytapi
    xmlgen = XMLGenerator()
    pytapi.sendDataBySEP(name, xmlgen.sendText(title=phone.title, prompt=phone.prompt, text=phone.text))
    return phone


@app.post("/phone/{name}/ring/")
async def create_item(name: str, phone: PhoneRingData):
    global pytapi
    xmlgen = XMLGenerator()
    pytapi.sendDataBySEP(name, xmlgen.ring(tone=phone.tone))
    return phone


@app.post("/phone/{name}/preparecall/")
async def create_item(name: str, phone: PhonePrepareCallData):
    global pytapi
    xmlgen = XMLGenerator()
    pytapi.sendDataBySEP(name, xmlgen.preparecall(name=phone.targetname, dn=phone.targetdn))
    return phone
