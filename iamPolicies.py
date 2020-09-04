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

# Retrieve details on a service ID, including history
def getServiceID(iam_token, service_id):
    url = 'https://iam.cloud.ibm.com/v1/serviceids/'+service_id
    headers = { "Authorization" : "Bearer "+iam_token, "accept": "application/json" }
    payload = {"include_history": "true"}
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

# Retrieve details on a service ID and print information - for now as JSON
def handleServiceID(iam_token, policy):
    for attr in policy["resources"][0]["attributes"]:
        #print(json.dumps(attr, indent=2))
        if (attr["name"] == "resourceType" and attr["value"] == "serviceid"):
            for attr2 in policy["resources"][0]["attributes"]:
                if (attr2["name"] == "resource"):
                    print(json.dumps(getServiceID(iam_token, attr2["value"]), indent=2))

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
def getPoliciesForUser(iam_token, account_id, iam_id, extended):
    apolicies=getAccessPolicies(iam_token, account_id, user_iam_id=iam_id)
    logging.info(json.dumps(apolicies, indent=2))
    for apolicy in apolicies["policies"]:
        prettyPolicy(apolicy)
        if (extended):
            handleServiceID(iam_token, apolicy)


# General help
def printHelp(progname):
    print ("Usage: "+progname+" --cred credential-file [--user iam_id] [--ext]")

# Get some parameters, then process the steps
if __name__== "__main__":
    credfile=None
    userID=None
    extended=False
    numArgs=len(sys.argv)
    if (numArgs<3 or numArgs>6):
        printHelp(sys.argv[0])
        exit()
    i=1
    while (i<numArgs):
        if (sys.argv[i]=="--ext"):
            extended=True
        elif (sys.argv[i]=="--cred" and (i+1<numArgs)):
            credfile=sys.argv[i+1]
            i+=1
        elif (sys.argv[i]=="--user" and (i+1<numArgs)):
            userID=sys.argv[i+1]
            i+=1
        else:
            print("wrong option")
            printHelp(sys.argv[0])
            exit()
        # increment    
        i+=1
        
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
    getPoliciesForUser(iam_token=iam_token, account_id=account_id, iam_id=userID, extended=extended)