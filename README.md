# Cisco Talos Blog Parser to Casebook

This is a sample script how to parse the Talos blogs, and automatically add observables to Cisco Casebook.

## Overview
1. The script leverages the Talos Blog RSS feed to retrieve all the current blogs.
2. It will then check if this is the first time the script runs.
  * If the script runs for the first time, it will parse through all blogs.
  * If the script has run before, it will check if there was an update to the blog (using the “last_modified” element from RSS).
    * If the was an update -> parse all the new blogs.
    * If there was no update -> do nothing.
3. During the parsing of the blog, noise is removed like hyperlinks to other webpages (e.g. Snort.org).
4. After this the CTR API is used to retrieve all the observables from the cleaned blog.
5. The last step is to create a CTR Casebook with the retrieved observables.


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
12. Make sure that the config.json file looks liks this:

  ```
  {
      "client_id": "client-XXXXXX-XXXX-XXXX-XXXX-XXXXXXXX",
      "client_secret": "XxXXxXXX_XXXX_XXxXX-XXXxX-XXXxXxXXXxX",
      "last_etag": "",
      "last_modified": ""
  }
  ```
  
13.  You are now ready to execute the script. Go to a terminal and change directory in to the folder that contains your **rss_feed_to_casebook.py** and **config.json** file. 
14. Make sure you have the correct libraries installed by executing the **requirements.txt** file (use a Python virtual environment if preferred: 

  ```
  pip3 install -r requirements.txt
  ```
  
15. Now execute the **rss_feed_to_casebook.py** script:

  ```
  python3.6 rss_feed_to_casebook.py
  ```

16. You are now done. Please feel free to have to use **crontab** to run the script every day. The script will handle this, and only create a new casebook if a new blog is added.
