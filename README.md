# Cisco Talos Blog Parser to Casebook

This is a sample script how to parse the Talos blogs, and automatically add observables to Cisco Casebook. The enables Security Researchers and Threat Responders in a SOC to quickly see if the observables from Talos have been seen in their environment (by leveraging Cisco Threat Response (CTR)). For more information on how to use CTR, please review this link: https://visibility.amp.cisco.com/#/help/introduction

## Overview
1. The script leverages the Talos Blog RSS feed to retrieve all the current blogs.
2. It will then check if this is the first time the script runs:
   * If the script runs for the first time, it will parse through all blogs.
   * If the script has run before, it will check if there was an update to the blog (using the “last_modified” element from RSS).
     * If the was an update -> parse all the new blogs.
     * If there was no update -> do nothing.
3. During the parsing of the blog, noise is removed like hyperlinks to other webpages (e.g. Snort.org). This greatly decreases false positives in the casebooks.
4. After this the CTR API is used to retrieve all the observables from the cleaned blog.
5. The last step is to create a CTR Casebook with the retrieved observables. The title of the blog and the link to the blog, will be added into the Case. Optionally a Webex Teams message is sent to a room to update the Threat Responder.


## Installation
1. Clone this repository or download the ZIP file.
2. Log in to https://visibility.amp.cisco.com/ with you Cisco Security credentials.
3. Make sure that you have Casebook enabled (+ the Casebook AMP, Threat Grid and Chrome widget, for extended functionality). Please find more information here: https://visibility.amp.cisco.com/#/help/casebooks
4. Click on **Modules**.
5. Click on **API Clients**.
6. Click on **Add API Credentials**.
7. Give the API Credentials a name (e.g. *Talos Blog Parser*).
8. Select on at least the **Casebook** and **Private Intelligence** checkboxes, however to be sure you can also click **Select All**.
9. Add an optional description if needed.
10. Click on **Add New Client**.
11. The **Client ID** and **Client Secret** are now shown to you. Do NOT click on **close** until you have copy pasted these credentials to the config.json file in the repository.
12. It is possible to integrate the script with Webex Teams. In order to do that, an API Access Token and a Room ID needs to be entered in the config.json file. Please retrieve your key from: https://developer.webex.com/docs/api/getting-started. Then create a dedicated Webex Teams space for these notifications and retrieve the Room ID from: https://developer.webex.com/docs/api/v1/rooms/list-rooms.
13. Make sure that the config.json file looks liks this (with the right keys and ID's filled in between the quotes):

  ```
  {
      "client_id": "<your_client_id>",
      "client_secret": "<your_client_secret",
      "last_etag": "",
      "last_modified": "",
      "webex_access_token": "<your_webex_access_token>",
      "webex_room_id": "<your_webex_room_id"
  }
  ```
  
14.  You are now ready to execute the script. Go to a terminal and change directory in to the folder that contains your **rss_feed_to_casebook.py** and **config.json** file. 
15. Make sure you have the correct libraries installed by executing the **requirements.txt** file (use a Python virtual environment if preferred): 

  ```
  pip3 install -r requirements.txt
  ```
  
16. Now execute the **rss_feed_to_casebook.py** script:

  ```
  python3.6 rss_feed_to_casebook.py
  ```

17. You are now done. 

## Notes and Road Map
* Please feel free to have to use **crontab** to run the script every day. The script will handle this, and only create a new casebook if a new blog is added. There is detailed information on how to use that here: https://pypi.org/project/python-crontab/. 
* Otherwise you can also use a function I previously wrote, which is the **intervalScheduler** function in this script: https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/VERSION-3.0/O365WebServiceParser.py. 
* This script works with the Talos RSS feed, but potentially it will also work with other RSS feeds. You will need to change the **url_feed** variable to another RSS feed. Also, you might need to clean the hyperlinks etc. out of the blogs in a different way (even though I am doing this quite generic).
* I will keep updating this script and otherwise you can also do a pull request with an update.
