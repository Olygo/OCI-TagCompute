# coding: utf-8

import oci
import os 
from os import system, name

##########################################################################
# set colors
##########################################################################

black='\033[0;30m'
red='\033[0;31m'
green='\033[0;32m'
yellow='\033[0;33m'
blue='\033[0;34m'
magenta='\033[0;35m'
cyan='\033[0;36m'
white='\033[0;37m'
default_c='\033[0m'

##########################################################################
# clear shell screen
##########################################################################

def clear():
    # -----------------------------
    # for windows
    # -----------------------------
    if name == 'nt':
        system('cls')

    # -----------------------------
    # for mac and linux(here, os.name is 'posix')
    # -----------------------------
    else:
        system('clear')

##########################################################################
# expand local path
##########################################################################

def path_expander(path):

    path = os.path.expanduser(path)
    
    return path

##########################################################################
# get tenancy name
##########################################################################

def get_tenancy(tenancy_id, config, signer):
    identity = oci.identity.IdentityClient(config=config, signer=signer)
    try:
        tenancy = identity.get_tenancy(tenancy_id)
        #print(tenancy.data)

    except Exception as e:
        print(red)
        print(e)
        print(default_c)
        raise SystemExit    

    return tenancy.data.name, tenancy.data.home_region_key

##########################################################################
# create signer for Authentication
# input - config_profile and is_instance_principals and is_delegation_token
# output - config and signer objects
##########################################################################

def create_signer(config_file_path, config_profile, is_delegation_token, is_config_file):

    # --------------------------------
    # Config File authentication
    # --------------------------------
    if is_config_file:
        try:
            config = oci.config.from_file(file_location=config_file_path, profile_name=config_profile)
            oci.config.validate_config(config) # raise an error if error in config

            signer = oci.signer.Signer(
                tenancy=config['tenancy'],
                user=config['user'],
                fingerprint=config['fingerprint'],
                private_key_file_location=config.get('key_file'),
                pass_phrase=oci.config.get_config_value_or_default(config, 'pass_phrase'),
                private_key_content=config.get('key_content')
            )

            print(green+f"{'*'*5:5} {'Login:':15} {'success':20} {'config file':40} {'*'*5:5}")
            print(green+f"{'*'*5:5} {'Login:':15} {'profile':20} {config_profile:40} {'*'*5:5}")
            
            oci_tname, oci_tregion = get_tenancy(config['tenancy'], config, signer)
            print(green+f"{'*'*5:5} {'Tenancy:':15} {oci_tname:20} {'home region: '+ oci_tregion:40} {'*'*5:5}")

            return config, signer, oci_tname
            
        except:
            print(red)
            print('\n****')
            print ("Authentication Error: check your Config file/profile")
            print(f"config_file: {config_file_path}")
            print(f"config_profile: {config_profile}")
            print('****\n')
            print(default_c)
            raise SystemExit

    # --------------------------------
    # Delegation Token authentication
    # --------------------------------
    elif is_delegation_token:

        try:
            # ------------------------------------------------------------------------------
            # check if env variables OCI_CONFIG_FILE, OCI_CONFIG_PROFILE exist and use them
            # ------------------------------------------------------------------------------
            env_config_file = os.environ.get('OCI_CONFIG_FILE')
            env_config_section = os.environ.get('OCI_CONFIG_PROFILE')
            config = oci.config.from_file(env_config_file, env_config_section)
            delegation_token_location = config['delegation_token_file']
            oci.config.validate_config(config) # raise an error if error in config

            with open(delegation_token_location, 'r') as delegation_token_file:
                delegation_token = delegation_token_file.read().strip()
                signer = oci.auth.signers.InstancePrincipalsDelegationTokenSigner(delegation_token=delegation_token)

            print(green+f"{'*'*5:5} {'Login:':15} {'success':20} {'delegation token':40} {'*'*5:5}")
            print(green+f"{'*'*5:5} {'Login:':15} {'token':20} {delegation_token_location:40} {'*'*5:5}")

            oci_tname, oci_tregion = get_tenancy(config['tenancy'], config, signer)
            print(green+f"{'*'*5:5} {'Tenancy:':15} {oci_tname:20} {'home region: '+ oci_tregion:40} {'*'*5:5}")

            return config, signer, oci_tname

        except:
            print(red)
            print ("Authentication Error: {Error obtaining delegation_token_file}")
            print(default_c)
            raise SystemExit

    # -----------------------------------
    # Instance Principals authentication
    # -----------------------------------
    else:
        try:
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            config = {'region': signer.region, 'tenancy': signer.tenancy_id}
            # print(signer.region)
            # print(signer.tenancy_id)
            oci_tname, oci_tregion = get_tenancy(config['tenancy'], config, signer)

            #oci.config.validate_config(config) # raise an error if error in config
            print(green+f"{'*'*5:5} {'Login:':15} {'success':20} {'instance principals':40} {'*'*5:5}")
            print(green+f"{'*'*5:5} {'Tenancy:':15} {oci_tname:20} {'home region: '+ oci_tregion:40} {'*'*5:5}")

            return config, signer, oci_tname

        except:
            print(red)
            print('\n****')
            print (f"Authentication Error: Instance Principals")
            print('****\n')
            print(default_c)
            raise SystemExit

##########################################################################
# get all compartments in the tenancy
##########################################################################

def get_compartment_list(identity_client, compartment_id):

    target_compartments = []
    all_compartments = []

    try:
        top_level_compartment_response = identity_client.get_compartment(compartment_id)
        target_compartments.append(top_level_compartment_response.data)
        all_compartments.append(top_level_compartment_response.data)
    
    except oci.exceptions.ServiceError as response:
        print(red)
        print('\n****')
        print (f"Error compartment_id: {compartment_id} : {response.code} - {response.message}")
        print('****\n')
        print(default_c)
        raise SystemExit

    while len(target_compartments) > 0:
        target = target_compartments.pop(0)

        child_compartment_response = oci.pagination.list_call_get_all_results(
            identity_client.list_compartments,
            target.id
        )
        target_compartments.extend(child_compartment_response.data)
        all_compartments.extend(child_compartment_response.data)

    active_compartments = []

    for compartment in all_compartments:
        if compartment.lifecycle_state== 'ACTIVE':
            active_compartments.append(compartment)
    
    return active_compartments

##########################################################################
# get all subscribed region in the tenancy
##########################################################################

def get_region_subscription_list(identity_client, tenancy_id, target_region):

    active_regions = identity_client.list_region_subscriptions(
        tenancy_id
    )

    if target_region != '':
        region_names=[]
        for region in active_regions.data:
            region_names.append(region.region_name)
        if target_region in region_names:
            pass
        else:
            print(red)
            print('\n****')
            print(f'Region {target_region} not subscribed or doesn"t exist...')
            print('****\n')
            print(default_c)
            raise SystemExit

    return active_regions.data

