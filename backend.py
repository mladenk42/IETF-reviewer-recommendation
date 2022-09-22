from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import datetime
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/html", StaticFiles(directory = "html"), name = "html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def logmessage(m):
    with(open("./log.txt", "a")) as logfile:
        logfile.write(str(datetime.datetime.now())  + " " + str(m) + "\r\n")

@app.get("/fetchCandidates")
async def fetchCandidates():
   try:
        logmessage("------------ Received request for candidate list ----------")
        content = open("./static/person_list.txt", "r", encoding = "utf-8").read()
        return content

   except Exception as e:
        logmessage("An exception occured: ")
        logmessage(e)
        logmessage("Returning FAIL")
        return {"FAIL"}

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
