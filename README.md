# IBM Cloud IAM Access Policies and Authorizations
The Python script [iamPolicies.py](iamPolicies.py) can be used to retrieve information about IBM Cloud IAM policies for Access Groups and direct Authorizations. It obtains the Access Group information and its policies for either the entire account or for the optionally passed in user (iam_id). The iam_id identifies a user or a service ID.

It makes use of two IBM Cloud API functions:
- [List IAM Access Groups](https://cloud.ibm.com/apidocs/iam-access-groups#list-access-groups)
- [List ](https://cloud.ibm.com/apidocs/iam-policy-management#list-policies)

To create a file with an API key which could be passed as credentials, use the following IBM Cloud CLI command:   
`ibmcloud iam api-key-create MY_API_KEY_NAME --file my__credentials.json --output json`

You can find the IAM ID of users with the following IBM Cloud CLI command:   
`ibmcloud account users --output json`

Information about service IDs can be retrieved using this command:   
`ibmcloud iam service-ids --output json`


### Sample usage and output

```
python3 iamPolicies.py my_credentials.json -u IBMid-55xxxxYP1X
Reading credentials
generating auth tokens


Access Groups:
=================================
Access Group:
  id:  AccessGroupId-a7b1b3a9-eb83-4ff8-xxxx-1234567890
  name:  cloud-network-admins
  description:  Create networks, VPCs, load balancers, subnets, firewall rules, and network devices.
Policy:
  Subject:  access_group_id  /  AccessGroupId-a7b1b3a9-eb83-4ff8-xxxx-1234567890
  Roles: 
     Viewer
  Resources:
   resourceType : resource-group
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-a7b1b3a9-eb83-4ff8-xxxx-1234567890
  Roles: 
     Administrator
  Resources:
   serviceName : is
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-a7b1b3a9-eb83-4ff8-xxxx-1234567890
  Roles: 
     Editor
  Resources:
   serviceName : support
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx

=================================
Authorizations:
Policy:
  Subject:  iam_id  /  IBMid-550007YP1X
  Roles: 
     Viewer
  Resources:
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
   serviceName : enterprise
```