#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Sensibo-Cli: a means of controlling the firmware of your Sensibo Air or Sky by way of a command-line interface.
    
    @Author: Nathaniel Schmidt <schmidty2244@gmail.com>
    Date created: 02/02/2022
    Date modified: 03/02/2022
    
    License: MIT <https://www.mit.edu/~amini/LICENSE.md>
"""

from argparse import ArgumentParser
import csv# Where we store the API key
import json
import requests

# globals:
_SERVER = 'https://home.sensibo.com/api/v2'

# Backend API access
class SensiboClientAPI:
    def __init__(self, api_key):
        self._api_key = api_key

    def _get(self, path, ** params):
        params['apiKey'] = self._api_key
        response = requests.get(_SERVER + path, params = params)
        response.raise_for_status()
        return response.json()

    def _patch(self, path, data, ** params):
        params['apiKey'] = self._api_key
        response = requests.patch(_SERVER + path, params = params, data = data)
        response.raise_for_status()
        return response.json()

    def devices(self):
        result = self._get("/users/me/pods", fields="id,room")
        return {x['room']['name']: x['id'] for x in result['result']}

    def pod_measurement(self, podUid):
        result = self._get("/pods/%s/measurements" % podUid)
        return result['result']

    def pod_ac_state(self, podUid):
        result = self._get("/pods/%s/acStates" % podUid, limit = 1, fields="status,reason,acState")
        return result['result'][0]['acState']

    def pod_change_ac_state(self, podUid, currentAcState, propertyToChange, newValue):
        self._patch("/pods/%s/acStates/%s" % (podUid, propertyToChange),
                json.dumps({'currentAcState': currentAcState, 'newValue': newValue}))

# Frontend interactions:
class App:
    def __init__ (self):
        self.filename = "api_keys.csv"
        self.file = None
        self.client = None
        self.key = None
        
        # Look for API key and if not found, then ask for it (https://fedingo.com/python-reading-writing-to-same-file/, https://stackabuse.com/file-handling-in-python/, https://realpython.com/python-csv/, https://www.section.io/engineering-education/files-and-exceptions-in-python/)
        while True:
            try:
                self.file = open (self.filename, 'r')
                self.reader = csv.DictReader (self.file)
                self.rows = 0
                for self.row in self.reader:
                    self.rows += 1
                
                if self.rows == 1:# We've only got one key stored, so let's just assume the user wants to use it, unless they specify otherwise
                    for self.row in self.reader:
                        self.key = self.reader['key']
                
                # else:
                    # Do something
                self.client = SensiboClientAPI (self.key)
                break
            except FileNotFoundError:
                self.apiKeyQuery = self.valInput ("It appears that you have not yet provided the program with your Sensibo API key. At least one API key is required for the program to be able to run. Would you like to enter one in? (Type Y for yes     or N for no)")
                while self.apiKeyQuery != "Y" and self.apiKeyQuery != "N":
                    print ("Pleas type 'Y' or 'N'.")
                    self.apiKeyQuery = self.valInput ("Want to enter the key in?")
                
                if self.apiKeyQuery == "Y":
                    self.file = open (self.filename, 'w')
                    self.keyName = input("What is the name for this key? You can use any name with letters, numbers or spaces, or specifically the name you entered into the Sensibo web app interface.")
                    self.key = input ("And what is the actual API key? You can type it in directly, or paste it in from the website.")
                    self.colHeads = ['name', 'key']
                    self.writer = csv.DictWriter (self.file, fieldnames = self.colHeads)
                    self.writer.writeheader ()
                    self.writer.writerow ({self.colHeads[0] : self.keyName, self.colHeads[1] : self.key})
                    self.file.close ()
                    print ("Done, API key has been stored.")
                else:
                    print ("Okay. Quitting program.")
                    exit ()
                continue
        
        self.mainPrompt = "Sensibo-cli> "
        self.query = self.valInput (self.mainPrompt)
        while self.query != "EXIT" and self.query != "QUIT":
            self.query = self.valInput (self.mainPrompt)
        else:
            exit ()
    
    def valInput (self, prompt):
        result = input (prompt)
        result = result.upper ()
        return result

if __name__ == "__main__":
    app = App ()