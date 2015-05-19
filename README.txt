************************** ADON Paper Middleware Service*****************************

See the following paper for the theory and details of the service implementation.
Network Personalization Service for Science Big Data 
Sripriya Seetharam, Prasad Calyam, Ronny Bazan Antequera, Longhai Cui,Saptarshi Debroy, Matthew Dickinson, Tsegereda Beyene

————————————————————————————————————————————————————————————

Current openflow controller is opendaylight, which only supports openflow 1.0 and installed in a windows server. A pox controller, which support openflow 1.3 features installed in a Linux server is preferred for modifying openflow rules through terminal.
Current openflow controller web interface Url http://128.206.116.172:8080/
Username: admin
Password: admin admin_2014.

————————————————————————————————————————————————————————————
Use xmlrpc protocol to support a distributed client–server model application structure. 

ADonService.py
ADON server runs on the the same machine in MU where the openflow controller is installed (128.206.116.172) and listens to the task quests from clients through port 8888. The server uses iperf to get the bandwidth of Layer 2 and Layer 3 connections between OSU DTN1 (128.146.162.35) and MU DTN2(128.206.117.1). It assigns traffic rules for application tasks from DTN2 for the best performance based on the real time Software Defined Monitoring information, rejects the task quests and put the task in the waiting task queue in the descending order of priority.  

ADonClient.py
ADON client runs on the nodes in the MU side such as DTN2 (128.206.117.1). ADonClient.py is specifically written for iRODS transfer application. Use python subprocess to call linux-like icommands, pass the name of the file needed to be transferred as the parameter. 

————————————————————————————————————————————————————————————
DTN1 (128.146.162.35)

1. Download the latest irods installation package.(Current version 3.3.1)

http://irods.org/download/

2. Unzip the installation package. 

tar zxvf irods3.3.1.tgz

3. Install iRODS system (Installation options - server)

./irodssetup

4. Ensure the following packages are installed: screen iperf3

sudo yum install screen iperf3

5. Start screen sessions for iperf3. 

screen -S ipef3_l2; iperf3 -s 12345; screen -d ipef3_l2;
screen -S ipef3_l3; iperf3 -s 54321; screen -d ipef3_l3;

6. If IPtables is running add the following rule to allow any traffic from DTN2

sudo nano /etc/sysconfig/iptables

-A INPUT -p tcp -s 128.206.117.1 -j ACCEPT
-A INPUT -p udp -s 128.206.117.1 -j ACCEPT
 
sudo service iptables restart

7. Specify the inbound port for the iRODS server.

sudo nano ~iRODS/config/irods.config
$SVR_PORT_RANGE_START = '59429';
$SVR_PORT_RANGE_END = '59429';



DTN2 (128.206.117.1)

1. Download the latest irods installation package.(Current version 3.3.1)

http://irods.org/download/

2. Unzip the installation package. 

tar zxvf irods3.3.1.tgz

3. Install iRODS system (Installation options - client)

./irodssetup

4. Ensure the following packages are installed: screen iperf3

sudo yum install screen iperf3

5. Go to iRODS command directory.

cd ~iRODS/clients/icommands/bin

6. Start screen sessions for ADON server.

screen -S AdonServer; python AdonServer.py; screen -d AdonServer;

7. Run the Adon Client with filename as parameter

python AdonClient.py filename 

