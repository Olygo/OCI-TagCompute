# OCI-TagCompute

**TagCompute** is a demonstration script showing you how to apply freeform tag to a resource.

# Quick install on Oracle Linux 7.9 

	curl https://raw.githubusercontent.com/Olygo/OCI-TagCompute/main/install.sh | bash

- install dependencies
- clone git repo locally
- schedule cron everyday at 11PM

# Features 
- **TagCompute** searches for compute instances, retrieves instance display name and adds a freeform tag with the following key/value:
	-  key: display_name
	-  value: *name-of-the-instance*

- **TagCompute** also tags compute related resources:
	- boot volume
	- block volumes
	- boot volume backups
	- block volume backups

- Support for using the script with Instance Principals. Meaning you can run this script inside OCI and when configured properly, you do not need to provide any details or credentials

-**Parameters for execution:**

```
-cs                  	authenticate through CloudShell Delegation Token
-cf                  	authenticate through local OCI config_file
-cfp  config_file     	change OCI config_file path, default: ~/.oci/config
-cp   config_profile  	indicate config file section to use, default: DEFAULT
-t    tag_key         	change key name to use in the freeform tag, default: display_name
-tlc  compartment_ocid   scan only a specific compartment, default: scan from root compartment
-rg   region_name  		scan only a specific region, default: scan all regions
-h,   --help           	show this help message and exit

```

# Install script into (free-tier) Autonomous Linux Instance

- Use an existing VCN or create a dedicated vcn (preferred) in a public or a private subnet (preferred if vpn or fastconnect)
- Create a free-tier compute instance using the Autonomous Linux 7.9 image
- Create a Dynamic Group called OCI_Scripting and add the OCID of your instance to the group, using this command:
```
	ANY {instance.id = 'OCID_of_your_Compute_Instance'}
```	

- Create a root level policy, giving your dynamic group permission to manage all-resources in tenancy:
```
	allow dynamic-group OCI_Scripting to manage all-resources in tenancy
```
- Login to your instance using an SSH connection
	- un the following commands:

```
  - sudo yum update -y
  - sudo yum install git -y
  - python3 -m pip install oci oci-cli --user
  - git clone https://github.com/Olygo/OCI-TagCompute.git
  - cd ./OCI-TagCompute
  - python3 OCI-TagCompute.py
```


# How to use
##### Default - No argument:
	
	python3 ./OCI-TagCompute.py

without arguments **OCI-TagCompute** tries to authenticate using Instance Principals

##### Authenticate with local_config_file:
	
	python3 ./OCI-TagCompute.py -cf

##### Authenticate with custom local_config_file & profile:
	
	python3 ./OCI-TagCompute.py -cf -cfp /home/opc/myconfig -cp MyDomain

##### Authenticate in cloud_shell:
	
	python3 ./OCI-TagCompute.py -cs

##### custom parameters example:
	
	python3 ./OCI-TagCompute.py -cf -rg eu-paris-1 -tlc ocid1.compartment.oc1..aaaaaaaaurxxxx -t TagName2023

Display all tagged resources
![Script Output](./output.png)

Instance tag
![Tag Instance](./taginstance.png)

Instance resources are also tagged (storage & backups)
![Tag Resource](./tagboot.png)

Filter cost analysis using freeform tag: display_name:XXXXX
![Cost Analysis](./costanalysis1.png)

See costs associated to all the resources attached to my instance (compute, storage, backup):
![Cost Analysis](./costanalysis2.png)


## Disclaimer
**Please test properly on test resources, before using it on production resources to prevent unwanted outages or unwanted bills.**
