import os

from oauth import authorize_creds

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def run_auth():
    for x in os.listdir("credential"):
        if x.endswith(".json"):
        # Prints only text file present in My Folder
            authorize_creds("credential/" + x)

if __name__ == '__main__':
    run_auth()
