# Dump out the IBM Cloud IAM Access Groups and Policies for 
# an iam_id (user or service ID). If no iam_id is passed as
# parameter, information for the entire account is dumped out.
#
# The script makes use of two IBM Cloud API functions:
# - https://cloud.ibm.com/apidocs/iam-access-groups#list-access-groups
# - https://cloud.ibm.com/apidocs/iam-policy-management#list-policies
#
# Use with iam_id being either user or service ID:
# python3 iamPolicies.py credentials.json -u iam_id
#
#
#
# Written by Henrik Loeser

import requests, json, sys, logging

# Read the API key from a credentials file
def readApiKey(filename):
    with open(filename) as data_file:
        credentials = json.load(data_file)
    api_key = credentials.get('apikey')
    return api_key

# Generate the required IAM access token
def getAuthTokens(api_key):
    url     = "https://iam.cloud.ibm.com/identity/token"
    headers = { "Content-Type" : "application/x-www-form-urlencoded" }
    data    = "apikey=" + api_key + "&grant_type=urn:ibm:params:oauth:grant-type:apikey"
    response  = requests.post( url, headers=headers, data=data )
    return response.json()


# Obtain information about the credentials
def getIAMDetails(api_key, iam_token):
    url     = "https://iam.cloud.ibm.com/v1/apikeys/details"
    headers = { "Authorization" : "Bearer "+iam_token, "IAM-Apikey" : api_key, "Content-Type" : "application/json" }
    response  = requests.get( url, headers=headers )
    return response.json()

# Which account are we working from? Need the account ID
def getAccounts(iam_token):
    url     = "https://accounts.cloud.ibm.com/v1/accounts"
    headers = { "Authorization" : "Bearer "+iam_token }
    response  = requests.get( url, headers=headers )
    return response.json()

# Obtain access groups and handle paging
def getAccessGroups(iam_token, account_id, user_iam_id=None):
    url = 'https://iam.cloud.ibm.com/v2/groups'
    # Empty transaction ID here in the code, but you could set it for better tracking
    headers = { "Authorization" : "Bearer "+iam_token, "accept": "application/json", "Transaction-Id":"" }
    payload = {"account_id": account_id, "iam_id": user_iam_id, "hide_public_access": "true", "limit": 100}
    response = requests.get(url, headers=headers, params=payload)
    groups=response.json()
    while ("next" in response.json()):
        response = requests.get(groups["next"]["href"], headers=headers)
        groups["groups"].extend(response.json()["groups"])
    return groups    

# Obtain the policies, either for an access group or related to an IAM ID (user, service ID)
def getAccessPolicies(iam_token, account_id, access_group_id=None, user_iam_id=None):
    url = 'https://iam.cloud.ibm.com/v1/policies'
    headers = { "Authorization" : "Bearer "+iam_token, "accept": "application/json" }
    payload = {"account_id": account_id, "access_group_id": access_group_id, "iam_id": user_iam_id}
    response = requests.get(url, headers=headers, params=payload)
    return response.json()    

# Some structured printing for groups
def prettyGroup(group):
    print("=================================")
    print("Access Group:")
    print("  id: ", group["id"])
    print("  name: ", group["name"])
    print("  description: ", group["description"])

# Some structured printing for a policy
def prettyPolicy(policy):
    print("Policy:")
    print("  Subject: ", policy["subjects"][0]["attributes"][0]["name"], " / ", policy["subjects"][0]["attributes"][0]["value"])
    print("  Roles: ")
    for role in policy["roles"]:
        print("    ", role["display_name"])
    print("  Resources:")
    for attr in policy["resources"][0]["attributes"]:
        print("  ",attr["name"],":",attr["value"])


# Handle Access Groups for a specific user or service ID
def getAccessGroupsForUser(iam_token, account_id, iam_id):
    agroups=getAccessGroups(iam_token=iam_token, account_id=account_id,user_iam_id=iam_id)
    logging.info(json.dumps(agroups, indent=2))
    for group in agroups["groups"]:
        logging.info(json.dumps(group, indent=2))
        prettyGroup(group)
        apolicies=getAccessPolicies(iam_token, account_id, access_group_id=group["id"])
        logging.info(json.dumps(apolicies, indent=2))
        for apolicy in apolicies["policies"]:
            prettyPolicy(apolicy)

# Handle Policies for a specific user or service ID
def getPoliciesForUser(iam_token, account_id, iam_id):
    apolicies=getAccessPolicies(iam_token, account_id, user_iam_id=iam_id)
    logging.info(json.dumps(apolicies, indent=2))
    for apolicy in apolicies["policies"]:
        prettyPolicy(apolicy)


# General help
def printHelp(progname):
    print ("Usage: "+progname+" credential-file [-u iam_id]")

# Get some parameters, then process the steps
if __name__== "__main__":
    credfile=None
    userID=None

    if (len(sys.argv)<2):
        printHelp(sys.argv[0])
        exit()
    elif (len(sys.argv)==2):
        credfile=sys.argv[1]
        mode=1
    elif (len(sys.argv)==4):
        credfile=sys.argv[1]
        if (sys.argv[2]=="-u"):
            mode=2
            userID=sys.argv[3]
        else:
            print ("wrong options")
            printHelp(sys.argv[0])
            exit()
    else:
        print ("unknown options")
        printHelp(sys.argv[0])
        exit()

    # Read the credentials (API key), then generate an auth token
    print ("Reading credentials")
    apiKey=readApiKey(credfile)
    print ("generating auth tokens")
    authTokens=getAuthTokens(api_key=apiKey)
    iam_token=authTokens["access_token"]   

    # Need to obtain the account ID
    accDetails=getIAMDetails(api_key=apiKey, iam_token=iam_token)
    account_id=accDetails['account_id']

    # Now process Access Groups, then direct Authorizations
    print("\n")
    print("Access Groups:")
    getAccessGroupsForUser(iam_token=iam_token, account_id=account_id, iam_id=userID)

    print("\n================================\nAuthorizations:")
    getPoliciesForUser(iam_token=iam_token, account_id=account_id, iam_id=userID)