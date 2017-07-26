TODO:

High level functionality (All will require a call to add an LDAP entry):

WebAppaS Creation:
  - Create a Hyper-V VM from a WebApp Template
  - Start Hyper-V VM
  - Create a Gitlab Repository
  - Generate appropriate SSH key data and send to the VM and Gitlab's configuration
  - Push a webapp template to Gitlab
  - Generate Credentials for DBaS DB and push to the VM
  - Create RT Ticket requesting DNS aliases (test and production)
  - Configure Reverse Proxy on IaaS
  - 
  - Regenerate SSL Certificates
  
VMaS Creation:
  - Create a Hyper-V VM with empty disk
  - Attach an Install Media Image to the VM
  - Generate


List of automated functionality and hooks which need to be built.

1. Creating Hyper-V VMs (Nextcloud, VMaS, WebAppAS at least)
- 

2. Adding LDAP entries 
- 

3. Creating Gitlab Projects
- 

4. Creating RT tickets for things we cannot automate
- 

5. Creating SQL DBs 
- 

6. Creating user accounts and associating permissions with DBs
- 
