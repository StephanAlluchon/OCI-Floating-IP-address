# Moving all IP secondary addresses from VNICs of VM#1 to VNICs of VM2#

# Version 0.9
# Author: stephan.alluchon@oracle.com
# We have 2 VM: VM1 and VM2. ALL Secondary privateIP will move from VNIC VM1 to VNIC VM2.

# We use flask on default port 5000 for HTTP server. when we receive an URL http://@IP:5000/ChangePrivateIP_basedOnIP
# we move a secondary private IP to a different VNIC in the same subnet
# So the HTTP request is the trigger
# API reference
# https://docs.cloud.oracle.com/iaas/api/#/en/iaas/20160918/PrivateIp/
# The goal is to manage High Availability for Third party services such as PaloAlto, F5...

# For this we use OCI SDK and Flask/waitress server.

# We also use a JSON file which is a configuration file
# In the configuration file, we provide IP addresses of the 2 VM which are sending simple HTTP request. PaloAlto Networks VM are able to send an HTTP request in case they need to do move from active to standby VM.
# The Python script analyzes IP source address of the request. Based on the IP source, it will move from VM1 to VM2 or the other side.

# You can test your JSON file and be sure atht you are using the right IP addresses with the python scripts:
# test_json_ip_address_SDK.py


import json
import oci
import email.utils
from oci.config import from_file
config = from_file(profile_name="yourprofile")
# need to run flask in virtual environnement pip install flask
from flask import Flask, request
from waitress import serve # needed for waitress

app = Flask(__name__)
app.debug = True   # need this for autoreload as and stack trace
with open('oci_value_IP_address.json') as json_file:  
    Entries = json.load(json_file)
# virtual_network = oci.core.VirtualNetworkClient(config)

def getPrivateIP (IP,MysubnetID):    
    print("\nRequesting:"+IP)
    getIP=virtual_network.list_private_ips(ip_address=IP, subnet_id=MysubnetID)
    JSON_ANSWER_raw=getIP.data
    error=0
    # Warning in private_ip.data there are som extra \n you need to remove    
    JSON_ANSWER=json.loads(str(JSON_ANSWER_raw).replace('\n',''))
    if getIP.status==200 and JSON_ANSWER!=[]:
        # print(">status code: "+str(getIP.status))
        vnicId=JSON_ANSWER[0].get('vnic_id')
        Id=JSON_ANSWER[0].get('id')
        # print(">"+vnicId)
        # print(">"+Id)
    else:
        error=1
        # print (">ERROR in request process")
        # print(">status code: "+str(getIP.status))
        if JSON_ANSWER==[]:
            print(">IP address not found!")
            vnicId=''
            Id=''
    return[vnicId,Id,error]

def changeIPsecondaryfromEntries2(NewPrimary):
    boolean=1
    messageHTTPfinal="HERE ARE ALL THE MODIFICATIONS:\n <br> "
    
    for i in EntriesIPonly:
        
        # try:
            if NewPrimary == 2:
                Current_privateIP=oci.core.models.UpdatePrivateIpDetails(vnic_id=i['IP2vnicId'])
                messageHTTP="{} is now on {}".format(i['IP3'],i['IP2'])
            elif NewPrimary == 1:
                Current_privateIP=oci.core.models.UpdatePrivateIpDetails(vnic_id=i['IP1vnicId'])
                messageHTTP="{} is now associated with {}".format(i['IP3'],i['IP1'])        
         
            responseGetList=virtual_network.update_private_ip(private_ip_id=i['IP3Id'], update_private_ip_details=Current_privateIP)
            status_code=responseGetList.status
            JSON_ANSWER_raw=responseGetList.data
            # Warning in private_ip.data there are som extra \n you need to remove    
            # JSON_ANSWER=json.loads(str(JSON_ANSWER_raw).replace('\n',''))

            print(JSON_ANSWER_raw)
            # response = requests.put(uri_update, auth=auth, headers=headers, data=body)
            
            print("Status CODE: "+str(status_code))
            if status_code==200:
                messageHTTPfinal=messageHTTPfinal+messageHTTP+"\n"+" <br> "
                print(i['IP3']+" is correclty updated")
            else:
                messageHTTPfinal=messageHTTPfinal+i['IP3']+" not updated! BAD RESPONSE STATUS CODE"
                print(i['IP3']+" is NOT updated. BAD RESPONSE STATUS CODE <br>")
        # except:
        #     boolean=0
        #     print("ERREUR SUR LA REQUETE DE "+i['VM3']+"\n")
        #     messageHTTPfinal=messageHTTPfinal+"ERREUR SUR LA REQUETE DE "+i['VM3']+"\n"+" <br> "
    return[boolean,messageHTTPfinal]

def getOCID():
    error=0
    for i in EntriesIPonly:
        print("IP Secondary: "+(i['IP3'])+"\n\n")      
        get_OCID=getPrivateIP(i['IP1'],i['MysubnetID'])
        error+=get_OCID[2]
        i['IP1vnicId']=get_OCID[0]
        i['IP1Id']=get_OCID[1]
        get_OCID=getPrivateIP(i['IP2'],i['MysubnetID'])
        error+=get_OCID[2]
        i['IP2vnicId']=get_OCID[0]
        i['IP2Id']=get_OCID[1]
        get_OCID=getPrivateIP(i['IP3'],i['MysubnetID'])
        error+=get_OCID[2]
        i['IP3vnicId']=get_OCID[0]
        i['IP3Id']=get_OCID[1]
    if error!=0:
        print(json.dumps(EntriesIPonly, sort_keys=True, indent=2))
        print ("\nERROR WHEN GETTING ALL OCID!\n")
        return[0]    
    else:
        print(json.dumps(EntriesIPonly, sort_keys=True, indent=2))
        print("No error on getting all OCID!")
        return[1]

@app.route('/ChangePrivateIP_VM1')
def primaryIsNow_VM1():
    print(request.environ['REMOTE_ADDR'])
    return_result=changeIPsecondaryfromEntries2(1)
    if return_result[0] == 1:
        message='Private IP updated!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {1} <br>
                    <blockquote>{2}</blockquote> <br>
                    {0}
                </h1>
            </body>
            </html>
            '''.format(message,email.utils.formatdate(usegmt=True),return_result[1])
    else:
        message='PrivateIP NON UPDATED!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {2} <br>
                    CODE STATUS {0} <br>
                    <blockquote>{3}</blockquote> <br>
                    {1}
                </h1>
            </body>
            </html>
            '''.format("KO",message,email.utils.formatdate(usegmt=True),return_result[1])

@app.route('/ChangePrivateIP_VM2')
def primaryIsNow_VM2():   
    print(request.environ['REMOTE_ADDR'])
    return_result=changeIPsecondaryfromEntries2(2)
    if return_result[0] == 1:
        message='Private IP updated!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {1} <br>
                    <blockquote>{2}</blockquote> <br>
                    {0}
                </h1>
            </body>
            </html>
            '''.format(message,email.utils.formatdate(usegmt=True),return_result[1])
    else:
        message='PrivateIP NON UPDATED!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {2} <br>
                    CODE STATUS {0} <br>
                    <blockquote>{3}</blockquote> <br>
                    {1}
                </h1>
            </body>
            </html>
            '''.format("KO",message,email.utils.formatdate(usegmt=True),return_result[1])

# the HTTP request must be http://@IP/ChangePrivateIP_basedOnIP    
@app.route('/ChangePrivateIP_basedOnIP')
def primaryIsBasedonIP():
    IPsource=request.environ['REMOTE_ADDR']
    print("IP Source: "+IPsource)
    if IPsource!=VM1PAN and IPsource!=VM2PAN:
        message='SOURCE IP is not from PAN VM!'
        print(message+"\n")
        return '''
                <html>
                <body>
                    <h1>
                        DATE: {2} <br>
                        CODE STATUS {0} <br>
                        {1}
                    </h1>
                </body>
                </html>
                '''.format("KO",message,email.utils.formatdate(usegmt=True))
    elif IPsource == VM1PAN:
        return_result=changeIPsecondaryfromEntries2(2)
        print("REQUEST FROM VM PAN 1")
    elif IPsource == VM2PAN:
        return_result=changeIPsecondaryfromEntries2(1)
        print("REQUEST FROM VM PAN 2")
    if return_result[0] == 1:
        message='Private IP updated!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {1} <br>
                    <blockquote>{2}</blockquote> <br>
                    {0}
                </h1>
            </body>
            </html>
            '''.format(message,email.utils.formatdate(usegmt=True),return_result[1])
    else:
        message='PrivateIP NON UPDATED!'
        print(message)
        print(return_result[1])
        return '''
            <html>
            <body>
                <h1>
                    DATE: {2} <br>
                    CODE STATUS {0} <br>
                    <blockquote>{3}</blockquote> <br>
                    {1}
                </h1>
            </body>
            </html>
            '''.format("KO",message,email.utils.formatdate(usegmt=True),return_result[1])



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
    
    getOCI_OK=getOCID()
    if getOCI_OK[0]==1:
        print ("Starting Flask server") 
        #app.run(host="0.0.0.0",port=5000)  
        serve(app, host='0.0.0.0', port=5000)
    else: 
        print ("Please Correct issue in JSON files")    
        
