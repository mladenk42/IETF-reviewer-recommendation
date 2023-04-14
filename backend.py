from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import datetime
from search.searchlib import IETF_recommender_API as recommender
from fastapi.staticfiles import StaticFiles
import pickle

app = FastAPI()

app.mount("/html", StaticFiles(directory = "html"), name = "html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rec = recommender()

def logmessage(m):
    with(open("./log.txt", "a")) as logfile:
        logfile.write(str(datetime.datetime.now())  + " " + str(m) + "\r\n")

@app.get("/fetchCandidates")
async def fetchCandidates():
   try:
        logmessage("------------ Received request for candidate list ----------")
        #content = open("./static/person_list.txt", "r", encoding = "utf-8").read()
        content = open("../indexing/data/person_list.txt", "r", encoding = "utf-8").read()
        return content

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"FAIL"}


@app.get("/fetchDraftCandidates")
async def fetchCandidates():
   try:
        logmessage("------------ Received request for draft candidate list ----------")
        d = pickle.load(open("../indexing/data/draft2topicvectors.pickle", "rb"))
        content = ";".join(list(d.keys()))
        return content

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"FAIL"}

@app.get("/log")
async def log(data: str):
   try:
        logmessage("------------ Received logging request ---------- : "  + data)

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"Something went wrong with the logging."}



@app.get("/search")
async def search(draft_name: str, model: str):
   try:
        print("CALLED")
        logmessage("------------ Received search request ---------- : default " + draft_name + " " + model)
        response_html = rec.search_default(draft_name, model)
        return response_html

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"Error during search. It has been logged and we will look into it."}


@app.get("/searchArea")
async def searchArea(draft_name: str, model: str, area: str):
   try:
        print("CALLED")
        logmessage("------------ Received search request ---------- : area" + draft_name + " " + model + " " + area)
        response_html = rec.search_area(draft_name, area, model)
        return response_html

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"Error during search. It has been logged and we will look into it."}


@app.get("/searchComp")
async def searchComp(draft_name: str, model: str, current: str):
   try:
        print("CALLED")
        logmessage("------------ Received search request ---------- : comp" + draft_name + " " + model + " " + current)

        
        response_html = rec.search_complementary(draft_name, current, model)
        return response_html
        #content = open("./static/person_list.txt", "r", encoding = "utf-8").read()
        #return content

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"Error during search. It has been logged and we will look into it."}







@app.get("/saveLabels")
async def saveLabels(jsondata: str):
    try:
        logmessage("------------ Received request for saving labels ----------")
        logmessage("Data received:")
        logmessage(jsondata)

        logmessage("Converting from string to dictionary.")
        data = json.loads(jsondata)
        dir_path = "./data/" + data["draft_name"]
        logmessage("Checking for draft folder. --> " + dir_path)
        if not os.path.exists(dir_path):
                logmessage("Draft folder not found, will create it.")
                os.mkdir(dir_path)
        else:
            logmessage("Folder was found.")
        logmessage("Starting the write process")
        for i in range(10000):
            file_name = dir_path + "/" + data["draft_name"] + "-" + str(i) + ".json"
            logmessage("Checking if name " + file_name + " is free.")
            if not os.path.exists(file_name):
                logmessage("Name was free, starting file write.")
                with open(file_name, "w") as outfile:
                    outfile.write(jsondata)
                logmessage("File write successful. Returning success: yes")
                return {"success": "yes"}
            else:
                logmessage("Name was not free, proceeding to next loop iteration.")
    except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning success: no")
        return {"success" : "no"}
