# coding: utf-8

##########################################################################
# name: OCI-TagCompute.py
# task: tag instances, boot/block volumes and backups using display_name of the instance
#
# author: Florian Bonneville
# version: 1.0 - march 14th 2023
#
# ***********************************************************************
# oci search for all resources using this tag :
# ***********************************************************************
# query
#   all resources
#     where
#       (freeformTags.key == 'display_name' && freeformTags.value == 'YOUR_INSTANCE_NAME')
# ***********************************************************************
#
# disclaimer: this is not an official Oracle application,  
# it does not supported by Oracle Support
##########################################################################

import oci
import argparse
from modules.identity import *
from modules.compute import *
from modules.tagging import *

##########################################################################
# get command line arguments
##########################################################################

parser=argparse.ArgumentParser()

#parser.add_argument('-ip', action='store_true', default=True, dest='is_instance_principals', help='Use Instance Principals for authentication')
parser.add_argument('-cs', action='store_true', default=False, dest='is_delegation_token', help='Use CloudShell Delegation Token for authentication')
parser.add_argument('-cf', action='store_true', default=False, dest='is_config_file', help='Use local OCI config file for authentication')
parser.add_argument('-cfp', default='~/.oci/config', dest='config_file_path', help='Path to your OCI config file, default: ~/.oci/config')
parser.add_argument('-cp', default='DEFAULT', dest='config_profile', help='config file section to use, default: DEFAULT')
parser.add_argument('-t', default='display_name', dest='tag_key', help='key value for the freeform tag')
parser.add_argument('-tlc', default='', dest='target_comp', help='compartment ocid to analyze, default is your root compartment')
parser.add_argument('-rg', default='', dest='target_region', help='region to analyze, default: all regions')

cmd = parser.parse_args()

##########################################################################
# clear shell screen
##########################################################################

clear()

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
# start printing header
##########################################################################

print()
print(green+f"{'*'*89:89}")
print(green+f"{'*'*5:5} {'Analysis:':15} {'started':20} {'OCI-TagCompute':40} {'*'*5:5}")

##########################################################################
# oci authentication
##########################################################################

config, signer, oci_tname=create_signer(cmd.config_file_path, cmd.config_profile, cmd.is_delegation_token, cmd.is_config_file)
tenancy_id=config['tenancy']

##########################################################################
# end printing header
##########################################################################

print(green+f"{'*'*89:89}\n")
print(f"{'REGION':15}  {'AD':6}  {'COMPARTMENT':20}  {'RESOURCE_TYPE':15}  {'RESOURCE_NAME':20}\n")

##########################################################################
# set top level compartment OCID to filter on a Compartment
##########################################################################

if cmd.target_comp:
    top_level_compartment_id=cmd.target_comp
else:
    top_level_compartment_id=tenancy_id

##########################################################################
# init oci service clients
##########################################################################

identity_client=oci.identity.IdentityClient(config=config, signer=signer)
obj_storage_client=oci.object_storage.ObjectStorageClient(config=config, signer=signer)

my_compartments=get_compartment_list(identity_client, top_level_compartment_id)
all_regions=get_region_subscription_list(identity_client, tenancy_id, cmd.target_region)


##########################################################################
# start analysis
##########################################################################

for region in all_regions:    
    s=' '*50
    config['region']=region.region_name
    core_client=oci.core.ComputeClient(config=config, signer=signer)
    blk_storage_client=oci.core.BlockstorageClient(config=config, signer=signer)

    if cmd.target_region == '' or region.region_name in cmd.target_region:

        for compartment in my_compartments:
            print(default_c+'   {}: Analyzing compartment: {}'.format(region.region_name, compartment.name),end=s+'\r')
            all_instances=list_instances(core_client, compartment.id)

            for instance in all_instances:
                print(default_c+'   {}: Analyzing instance: {}'.format(region.region_name, instance.display_name),end=s+'\r')

                # retrieve instance tags
                freeform_tags_dict = instance.freeform_tags
                # add key/value to dict
                freeform_tags_dict.update({cmd.tag_key: instance.display_name})
                tag_resources('compute', core_client, instance.id, freeform_tags_dict)
                print(yellow+f"{region.region_name:15}  {instance.availability_domain[-4:]:6}  {compartment.name[0:18]:20}  {'instance':15}  {instance.display_name[0:18]:20}")

                # search for boot volumes                
                instance_bootvolattach=list_instances_bootvol(core_client, instance.availability_domain, compartment.id, instance.id)

                for bootvolattach in instance_bootvolattach:
                    bootvol=blk_storage_client.get_boot_volume(bootvolattach.boot_volume_id).data

                    # retrieve boot volume tags
                    freeform_tags_dict = bootvol.freeform_tags
                    # add key/value to dict
                    freeform_tags_dict.update({cmd.tag_key: instance.display_name})
                    tag_resources('bootvolume', blk_storage_client, bootvol.id, freeform_tags_dict)
                    print(yellow+f"{region.region_name:15}  {bootvol.availability_domain[-4:]:6}  {compartment.name[0:18]:20}  {'boot':15}  {bootvol.display_name[0:18]:20}")

                # search for boot volume backups
                boot_volume_backups=list_boot_volume_backups(blk_storage_client, compartment.id, bootvol.id)

                for boot_volume_backup in boot_volume_backups:
                    bootvolbkp=blk_storage_client.get_boot_volume_backup(boot_volume_backup.id).data

                    # retrieve boot volume backup tags
                    freeform_tags_dict = boot_volume_backup.freeform_tags
                    # add key/value to dict
                    freeform_tags_dict.update({cmd.tag_key: instance.display_name})
                    tag_resources('boot_backup', blk_storage_client, boot_volume_backup.id, freeform_tags_dict)
                    print(yellow+f"{region.region_name:15}  {'-':6}  {compartment.name[0:18]:20}  {'bootvolbkp':15}  {bootvolbkp.display_name[0:18]:20}")

                # search for volumes
                try:
                    instance_vol_attach=list_instances_volattach(core_client, instance.availability_domain, compartment.id, instance.id)

                    for vol_attach in instance_vol_attach:
                        volume=blk_storage_client.get_volume(vol_attach.volume_id).data

                        # retrieve volume tags
                        freeform_tags_dict = volume.freeform_tags

                        # add key/value to dict
                        freeform_tags_dict.update({cmd.tag_key: instance.display_name})
                        tag_resources('volume', blk_storage_client, volume.id, freeform_tags_dict)
                        print(yellow+f"{region.region_name:15}  {volume.availability_domain[-4:]:6}  {compartment.name[0:18]:20}  {'volume':15}  {volume.display_name[0:18]:20}")

                    # search for volume backups
                    volume_backups=list_volume_backups(blk_storage_client, compartment.id, volume.id)

                    for volume_backup in volume_backups:
                        volbkp=blk_storage_client.get_volume_backup(volume_backup.id).data

                        # retrieve volume backup tags
                        freeform_tags_dict = volume_backup.freeform_tags
                        # add key/value to dict
                        freeform_tags_dict.update({cmd.tag_key: instance.display_name})
                        tag_resources('volume_backup', blk_storage_client, volume_backup.id, freeform_tags_dict)
                        print(yellow+f"{region.region_name:15}  {'-':6}  {compartment.name[0:18]:20}  {'volbkp':15}  {volbkp.display_name[0:18]:20}")
                except:
                    pass # pass if no block volumes or backups found

# reset terminal color
print(' '*50)
print(default_c)