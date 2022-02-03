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
class App (SensiboClientAPI):
    def __init__ (self, api_key = None):
        super ().__init__(api_key)
        
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