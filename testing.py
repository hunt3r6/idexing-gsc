import os
from oauth import authorize_creds

for x in os.listdir("credential"):
    if x.endswith(".json"):
        # Prints only text file present in My Folder
        authorize_creds("credential/" + x)