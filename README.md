[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/chrivand/talos_blog_to_casebook)

# RSS Feed Blog Parser to Cisco Threat Response Casebook [v2.0]

This is a sample script to parse the Cisco Talos blog (and other blogs!), check for Target Sightings and automatically add observables to Cisco Casebook. This enables Security Researchers and Threat Responders in a SOC to quickly see if the observables from Talos have been seen in their environment (by leveraging Cisco Threat Response (CTR)). 

* For more information on how to use CTR, please review this link: [https://visibility.amp.cisco.com/#/help/introduction](https://visibility.amp.cisco.com/#/help/introduction).
* If you would like to see a demo of the script, please check out the video below: 

[https://youtu.be/cCe3y6XZqs0]()

[![Alt text](https://img.youtube.com/vi/cCe3y6XZqs0/0.jpg)](https://www.youtube.com/watch?v=cCe3y6XZqs0)

## Release notes version 2.0
1. The ciscospark library has been updated to the newer webexteamssdk library.
2. The script now also removes all clean observables from the case to stop false positives. Often legitimate websites are added in a blog, but are not an observable associated directly with the malware campaign. This causes Target Sightings, without them being of much interest. Removing these from the investigation is also better for the performance of the script. 
3. The script now also checks for Target Sightings. If there is a Sighting of a Target, the Webex Teams message and the Case description in Casebook will get a "HIGH PRIORITY" tag.
4. The script now has support for more RSS feeds. The FortiGuard and Unit42 RSS feeds have now been added as example (on top of the Talos RSS Feed).
5. The script will use the RSS feed "entry.link" to download the full blogpost, and does not just look at the "entry.description" of the RSS feed. The FortiGuard blog for example does not include the observables in their RSS feed, but only shows them on the actual original blog post.
6. Since the script has been expanded, it now can run longer than 10 minutes. This is actually the expiration time of the CTR OAuth token. Therefore, every API call now retrieves a new OAuth token.
7. The script has generally been cleaned up.

## Overview
1. The script leverages the Cisco Talos, FortiGuard and Unit42 blog RSS feeds (and/or other blogs) to retrieve all the current blogs.
2. It will then check if this is the first time the script has run:
   * If the script is being run for the first time, it will parse through all blogs.
   * If the script has run before, it will check if there was an update to the blog (using the “last_modified” element from RSS).
     * If there was an update -> parse all the new blogs.
     * If there was no update -> do nothing.
3.	During the parsing of the blog, an attempt is made to remove False Positives, like hyperlinks to other webpages (e.g., Snort.org). 
4. After this the CTR API is used to retrieve all the observables from the cleaned blog.
5. In version 2.0 it now removes observables with a clean disposition (retrieved from CTR API).
6. In version 2.0 it now also checks for Target Sightings. If there is a Sighting of a Target, the Webex Teams message and the Case description in Casebook will get a "HIGH PRIOIRTY" tag.
5. The last step is to create a CTR Casebook with the retrieved observables. The title of the blog and the link to the blog will be added into the Case. Optionally, a Webex Teams message is sent to a room to update the Threat Responder.


## Installation
1. Clone this repository or download the ZIP file.
2. Log in to [https://visibility.amp.cisco.com/](https://visibility.amp.cisco.com/) with your Cisco Security credentials.
3. Make sure that you have Casebook enabled (+ the Casebook AMP, Threat Grid and Chrome widget, for extended functionality). Please find more information here: [https://visibility.amp.cisco.com/#/help/casebooks](https://visibility.amp.cisco.com/#/help/casebooks).
4. Click on **Modules**.
5. Click on **API Clients**.
6. Click on **Add API Credentials**.
7. Give the API Credentials a name (e.g., *Talos Blog Parser*).
8. Select at least the **Casebook** and **Private Intelligence** checkboxes; however, to be sure, you can also click **Select All**.
9. Add an optional description if needed.
10. Click on **Add New Client**.
11. The **Client ID** and **Client Secret** are now shown to you. Do NOT click on **close** until you have copy-pasted these credentials to the config.json file in the repository.
12. It is possible to integrate the script with Webex Teams. In order to do that, an API Access Token and a Room ID need to be entered in the config.json file. Please retrieve your key from: [https://developer.webex.com/docs/api/getting-started](https://developer.webex.com/docs/api/getting-started). Then create a dedicated Webex Teams space for these notifications and retrieve the Room ID from: [https://developer.webex.com/docs/api/v1/rooms/list-rooms](https://developer.webex.com/docs/api/v1/rooms/list-rooms). Please be aware that the personal token from the getting started page only works for 12 hours. Please follow these steps to request a token per request: [https://developer.webex.com/docs/integrations](https://developer.webex.com/docs/integrations). This is roadmapped for v3.0 of the script.
13. Make sure that the config.json file looks like this (with the right keys and IDs filled in between the quotes):

  ```
  {
      "client_id": "<your_client_id>",
      "client_secret": "<your_client_secret>",
      "last_etag": "",
      "last_modified": "",
      "webex_access_token": "<your_webex_access_token>",
      "webex_room_id": "<your_webex_room_id",
      "url_feeds": [
        {
            "feed_name": "[Talos RSS Feed]",
            "rss_url": "http://feeds.feedburner.com/feedburner/Talos",
            "last_etag": "",
            "last_modified": 0
        },
        ... 
  }
  ```
  
14.  You are now ready to execute the script. Go to a terminal and change directory to the folder that contains your **rss_feed_to_casebook.py** and **config.json** file. 
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
* Please feel free to use **crontab** to run the script every day. The script will handle this and create a new casebook only if a new blog is added. There is detailed information on how to use crontab here: [https://pypi.org/project/python-crontab/](https://pypi.org/project/python-crontab/). 
* Otherwise, you can also use a function I previously wrote, which is the **intervalScheduler** function in this script: [https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/VERSION-3.0/O365WebServiceParser.py](https://github.com/chrivand/Firepower_O365_Feed_Parser/blob/VERSION-3.0/O365WebServiceParser.py). 
* This script works with the Talos, FortiGuard and Unit42 RSS feed, but potentially it will also work with other RSS feeds. You will need to add or change the **url_feeds** variable (in config.json) with another RSS feed. Also, you might need to clean the hyperlinks, etc., out of the blogs in a different way (even though I am doing this quite genericly).
* I will keep updating this script and you can also do a pull request with an update.
* Please open an "Issue" if there is something not working or if you have a feature request.
* Currently the Webex Teams Authentication works with a temporary token. This will be improved with an official Webex Teams Integration (roadmapped for v3.0).
