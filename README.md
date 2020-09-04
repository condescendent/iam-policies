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

Note that to access existing policies you need to be account owner or have Viewer role on all IAM-enabled services and on Account Management services. This includes the IAM Access Groups Service which is required to retrieve IAM Access Groups.

### Sample usage and output
The following shows the output when invoked for a user with ID IBMid-55xxxxYP1X.

```
python3 iamPolicies.py --cred my_credentials.json --user IBMid-55xxxxYP1X
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

Sample output when invoked for a service ID:

```
python3 iamPolicies.py --cred ~/.bluemix/apiKey_20206_Henrik_TF.json --user iam-ServiceId-a4bc6311-bc05-41e4-xxxx-1234567890
Reading credentials
generating auth tokens


Access Groups:
=================================
Access Group:
  id:  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  name:  cloud-app-services
  description:  Create app-related resources and services, mostly through a service ID.
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Writer
  Resources:
   serviceName : cloud-object-storage
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Writer
  Resources:
   serviceName : kms
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Writer
  Resources:
   serviceName : appid
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Editor
  Resources:
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Viewer
  Resources:
   serviceName : is
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Viewer
     Reader
  Resources:
   resourceType : resource-group
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Administrator
     Manager
     Writer
     Viewer
  Resources:
   serviceName : containers-kubernetes
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
Policy:
  Subject:  access_group_id  /  AccessGroupId-6412c1e3-b8f8-42fc-zzzz-0123456789
  Roles: 
     Manager
  Resources:
   serviceName : cloudantnosqldb
   resourceGroupId : 112b62f6d4ea4a9883f1b6b2288faf6e
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx

================================
Authorizations:
Policy:
  Subject:  iam_id  /  iam-ServiceId-a4bc6311-bc05-41e4-yyyy-0987654321
  Roles: 
     Administrator
  Resources:
   accountId : axxx89015fbbc37c99e3a9xxxxxxxxxx
   serviceName : iam-identity
   resourceType : serviceid
   resource : ServiceId-5a2890af-9ae1-497a-aaaa-8729d3e9c229
```