print("\n\n***************\n\nCREATED BY CHRISTOPHER VAN DER MADE (CHRIVAND)\n\n***************\n\n")

# NOTE: this is a Proof of Concept script, please test before using in production!

# Copyright (c) 2017 Cisco and/or its affiliates.
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at
#                https://developer.cisco.com/docs/licenses
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import requests
import json
import feedparser
import config
#import time
from datetime import datetime
import os
import ciscosparkapi

### this function opens config.json
def open_config():
    if os.path.isfile("config.json"):
        global config_file
        with open("config.json", 'r') as config_file:
            config_file = json.loads(config_file.read())
            print("\nThe config.json file was loaded.\n")
    else:
        print("No config.json file, please make sure config.json file is in same directory.\n")

### this function writes to config.json
def write_config():
    with open("config.json", 'w') as output_file:
        json.dump(config_file, output_file, indent=4)

### this function requests access token for OAuth2 for other CTR API requests
def get_CTR_access_token(client_id,client_secret):
    # create headers for access token request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }

    data = {
    'grant_type': 'client_credentials'
    }

    # create headers for access token request
    response = requests.post('https://visibility.amp.cisco.com/iroh/oauth2/token', headers=headers, data=data, auth=(client_id, client_secret))

    #check if request was succesful
    if response.status_code == 200:
        
        # grab the text from the request
        rsp_dict = json.loads(response.text)
        # retrieve variables from text, global variable so that it can be used by all functions for CTR
        global access_token
        access_token = (rsp_dict['access_token'])
        scope = (rsp_dict['scope'])
        expiration_time = (rsp_dict['expires_in'])     
        # user feedback
        print(f"[200] Success, access_token generated!\n \nThis is the scope: {scope}\n \nThe access token expires in: {expiration_time} seconds\n") 
    else:
        # user feedback
        print(f"Access token request failed, status code: {response.status_code}\n")

### this function removes hyperlinks and other false positives from a blog post
def clean_entry(entry_description):
    
    # split text into words
    words_entry = entry_description.split() 
    
    # create empty list for words which do not contain any of the below noise + for every entry clear it again
    cleaned_entry = []

    # remove noise from blogs (hyperlinks etc.)
    for word in words_entry:
        if word.startswith('href="'):
            pass
        elif word.startswith('src="'):
            pass
        elif word.startswith('xmlns:'):
            pass
        elif word.startswith('url="'):
            pass
        elif word.startswith('Snort.org'):
            pass
        else:
            cleaned_entry.append(word)
    
    # stitch the blog back together (list of words to string)
    space_words = " "
    cleaned_entry_str = space_words.join(cleaned_entry)

    # return cleaned string that contains all words (needed to retrieve observables)
    return cleaned_entry_str


### this function parses a RSS feed into raw text
def parse_rss_feed(url_feed):

    # store the etag and modified
    if config_file['last_etag'] == '' or config_file['last_modified'] == '':
        # user feedback
        print("First time script runs, no last version stored. Parsing through all available blogs now...\n")
        
        # retrieve all blogs and store info in config.json to check for updates in subsequent script runs
        response = feedparser.parse(url_feed)
        config_file['last_etag'] = response.etag
        config_file['last_modified'] = list(response.modified_parsed)
        write_config()

        # run through all entries and create casebook per entry     
        for entry in response.entries:

            # send the description of the blog entry (containing the body) to cleaning function to remove hyperlinks etc.
            cleaned_entry_str = clean_entry(entry.description)

            # retrieve observables
            returned_observables = return_observables(cleaned_entry_str,access_token)

            # retrieve title for casebook indexing              
            entry_title = entry.title

            # retrieve link for casebook description
            entry_link = entry.link

            # if observables were returned (list not empty), create a casebook
            if returned_observables != "[]":
                new_casebook(returned_observables,entry_title,entry_link,access_token)
            else:
                print(f"No new casebook created (no observables found) from: {entry_title}\n")
              
    # tags were stored, so check if new entries on RSS feed
    else:
        # check if new version exists
        response_update = feedparser.parse(url_feed, etag=config_file['last_etag'], modified=config_file['last_modified'])

        if response_update.status == 304:
            # no changes if status is 304
            print("No changes to RSS feed detected...\n")
        else:
            response = feedparser.parse(url_feed)
            print(f"Change detected, last modified: {response.modified}, checking for new blogs to parse...\n")

            # run through all entries and create casebook per entry     
            for entry in response.entries:

                # check if the blog is newer than then last one
                if list(entry.published_parsed) > config_file['last_modified']:

                    # user feedback
                    print(f"Blog detected that was published later than last modified: {entry.title}\n")

                    # send the description of the blog entry (containing the body) to cleaning function to remove hyperlinks etc.
                    cleaned_entry_str = clean_entry(entry.description)

                    # retrieve observables
                    returned_observables = return_observables(cleaned_entry_str,access_token)

                    # retrieve title for casebook indexing              
                    entry_title = entry.title

                    # retrieve link for casebook description 
                    entry_link = entry.link

                    # if observables were returned (list not empty), create a casebook
                    if returned_observables != "[]":
                        new_casebook(returned_observables,entry_title,entry_link,access_token)
                    else:
                        print(f"No new casebook created (no observables found) from: {entry_title}\n")

                else:
                    print(f"Blog has already been parsed: {entry_title}.\n")

            # set new values in config.json file
            config_file['last_etag'] = response.etag
            config_file['last_modified'] = list(response.modified_parsed)
            write_config()
    return
    
### this function will parse raw text and return the observables and types
def return_observables(raw_text,access_token):

    bearer_token = 'Bearer ' + access_token

    headers = {
        'Authorization': bearer_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    data = json.dumps({"content":raw_text})

    response = requests.post('https://visibility.amp.cisco.com/iroh/iroh-inspect/inspect', headers=headers, data=data)
    #check if request was succesful
    if response.status_code == 200:
        return(response.text) 
    else:
        print(f"Observable parsing request failed, status code: {response.status_code}\n")

### this function post list of observables to new casebook
def new_casebook(returned_observables,entry_title,entry_link,access_token):

    bearer_token = 'Bearer ' + access_token

    headers = {
        'Authorization': bearer_token,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    # create title and description for SOC researcher to have more context
    casebook_title = "New Case added by RSS_feed: " + entry_title
    casebook_description = "Python generated casebook (Talos RSS_feed): " + entry_link
    casebook_datetime = datetime.now().isoformat() + "Z"

    # create right json format to create casebook
    casebook_json = json.dumps({
        "title": casebook_title,
        "description": casebook_description,
        "observables": json.loads(returned_observables),
        "type": "casebook",
        "timestamp": casebook_datetime   
    })

    # post request to create casebook
    response = requests.post('https://private.intel.amp.cisco.com/ctia/casebook', headers=headers, data=casebook_json)
    if response.status_code == 201:
        print(f"[201] Success, casebook added: {entry_title}\n")
        
        # if Webex Teams tokens set, then send message to Webex room
        if config_file['webex_access_token'] is '' or config_file['webex_room_id'] is '':

            # user feed back
            print("Webex Teams not set.\n\n")
        else:            
            # instantiate the Webex handler with the access token
            webex = ciscosparkapi.CiscoSparkAPI(config_file['webex_access_token'])

            # post a message to the specified Webex room 
            try:
                message = webex.messages.create(config_file['webex_room_id'], text=casebook_title)
            # error handling, if for example the Webex API key expired
            except Exception:
                print("Webex authentication failed... Please make sure Webex Teams API key has not expired. Please review developer.webex.com for more info.\n")
    else:
        print(f"Something went wrong while posting the casebook to CTR, status code: {response.status_code}\n")

    return response.text

### main script 
if __name__ == "__main__":
    try:
        # open config json file and grab client_id and secret
        open_config()
        
        #error checking for API client details
        if config_file['client_id']:
            client_id = config_file['client_id']
        else:
            print("client_id is missing in config.json file...\n")

        if config_file['client_secret']:
            client_secret = config_file['client_secret']
        else:
            print("client_secret is missing in config.json file...\n")

        # generate access token to be used in other functions.
        get_CTR_access_token(client_id,client_secret)

        # activate the RSS feed parser for the Talos blog
        url_feed = config_file['url_feed']
        parse_rss_feed(url_feed)

    except KeyboardInterrupt:
        print("\nExiting...\n")




