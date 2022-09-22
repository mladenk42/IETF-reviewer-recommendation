# IETF-reviewer-recommendation

This repository contains the annotation app for suitable reviewers for IETF drafts.

Quickstart:
1. clone the repository
2. install requirements (best into a virtual python environment, development was done using Python version 3.9.4)
   pip install fastapi, uvicorn
3. edit "start.sh" to determine the address and port to listen on and execute it to run the server

The annotation interface should now be available at something like: http://yourhost.com:12345/html/index.html
