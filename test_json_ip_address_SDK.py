# Version 0.9
# Author: stephan.alluchon@oracle.com
# Test of JSON file with API clal on OCI
# API reference
# https://docs.cloud.oracle.com/iaas/api/#/en/iaas/20160918/PrivateIp/



# pip install httpsig_cffi requests six
# import httpsig_cffi.sign

import json
import oci
from oci.config import from_file
config = from_file(profile_name="yourprofile")
# need to run flask in virtual environnement pip install flask
from flask import Flask, request

app = Flask(__name__)
app.debug = True   # need this for autoreload as and stack trace
with open('oci_value_IP_address.json') as json_file:  
    Entries = json.load(json_file)
virtual_network = oci.core.VirtualNetworkClient(config)

def getPrivateIP (IP,MysubnetID):
    
    print("\nRequesting:"+IP)
    getIP=virtual_network.list_private_ips(ip_address=IP, subnet_id=MysubnetID)
    JSON_ANSWER_raw=getIP.data
    error=0
    # Warning in private_ip.data there are som extra \n you need to remove    
    JSON_ANSWER=json.loads(str(JSON_ANSWER_raw).replace('\n',''))
    if getIP.status==200 and JSON_ANSWER!=[]:
        print(">status code: "+str(getIP.status))
        vnicId=JSON_ANSWER[0].get('vnic_id')
        Id=JSON_ANSWER[0].get('id')
        print(">"+vnicId)
        print(">"+Id)
    else:
        error=1
        print (">ERROR in request process")
        print(">status code: "+str(getIP.status))
        if JSON_ANSWER==[]:
            print(">IP address not found!")
            vnicId=''
            Id=''
    return[vnicId,Id,error]
        

if __name__ == '__main__':
    
    virtual_network = oci.core.VirtualNetworkClient(config)
    count=0
    EntriesIPonly=[]
    for i in Entries:
        if count==0:
            VM1PAN=i['VM1PAN']
            VM2PAN=i['VM2PAN']
        if count!=0:
            EntriesIPonly.append(i)
        count+=1

    for i in EntriesIPonly:
         # print("Secondary test: "+(i['VM3']))
        # try:
            List_VNICID=getPrivateIP(i['IP1'],i['MysubnetID'])
            List_VNICID=getPrivateIP(i['IP2'],i['MysubnetID'])
            List_VNICID=getPrivateIP(i['IP3'],i['MysubnetID'])
            
        #except:
        #    messageHTTPfinal=messageHTTPfinal+"ERREUR SUR LES CHAMPS "+i['VM3']+"\n"
    #print(Entries)
    #print("\n")
    #print(EntriesIPonly)        
    print("finish!")    
