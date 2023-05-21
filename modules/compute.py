# coding: utf-8

import oci

##########################################################################
# Set colors
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
# list all active instances
##########################################################################

def list_instances(core_client, compartment_id):

    Good_States=['RUNNING', 'STOPPED']
    my_instances=[]
    instances=oci.pagination.list_call_get_all_results(core_client.list_instances, compartment_id=compartment_id).data

    for instance in instances:
        if (instance.lifecycle_state in Good_States):
            # print(instance)
            # print(instance.region)
            # print(compartment.name)
            # print(instance.display_name)
            # print(instance.id)
            # print(instance.availability_domain)

            my_instances.append(instance)
    return my_instances

##########################################################################
# get boot volume for each instance
##########################################################################

def list_instances_bootvol(core_client, availability_domain, compartment_id, instance_id):
    
    my_bootvol=[]
    boot_volumes=oci.pagination.list_call_get_all_results(core_client.list_boot_volume_attachments,availability_domain=availability_domain, compartment_id=compartment_id, instance_id=instance_id).data

    for bootvol in boot_volumes:
        #if bootvol.lifecycle_state == 'ATTACHED':
            # print(bootvol)
            # print(bootvol.display_name)
            # print(bootvol.iboot_volume_idd)
            # print(bootvol.availability_domain)
            # print(bootvol.compartment_id)
            # print(bootvol.encryption_in_transit_type)
            # print(bootvol.instance_id)
            # print(bootvol.lifecycle_state)
            # print(bootvol.time_created)

        my_bootvol.append(bootvol)

    return my_bootvol

##########################################################################
# list all boot volume backups
##########################################################################

def list_boot_volume_backups(blk_storage_client, compartment_id, boot_volume_id):

    my_bootvol_backups=[]
    bootvol_backups=oci.pagination.list_call_get_all_results(blk_storage_client.list_boot_volume_backups, compartment_id=compartment_id, boot_volume_id=boot_volume_id).data
    
    for bootvolbkp in bootvol_backups:
        if bootvolbkp.lifecycle_state == 'AVAILABLE':
            # print(bootvolbkp.display_name)
            # print(bootvolbkp.lifecycle_state)
            # print(bootvolbkp.unique_size_in_gbs)
            # print(bootvolbkp.source_type)
            # print(bootvolbkp.time_created.strftime('%Y-%m-%d %H:%M:%S'))
            # print(bootvolbkp.type)

            my_bootvol_backups.append(bootvolbkp)
    return my_bootvol_backups


##########################################################################
# list all block volume attachement for each instance
##########################################################################

def list_instances_volattach(core_client, availability_domain, compartment_id, instance_id):
    
    volattachs=oci.pagination.list_call_get_all_results(core_client.list_volume_attachments,availability_domain=availability_domain, compartment_id=compartment_id, instance_id=instance_id).data
    my_blk_attach=[]

    for volattach in volattachs:
        # print(volattach)
        # print(volattach.id)
        # print(volattach.volume_id)

        my_blk_attach.append(volattach)
    return my_blk_attach

##########################################################################
# list all block volume backups
##########################################################################

def list_volume_backups(blk_storage_client, compartment_id, volume_id):

    my_blk_backups=[]

    items=oci.pagination.list_call_get_all_results(blk_storage_client.list_volume_backups, compartment_id=compartment_id, volume_id=volume_id).data
    
    for blkvolbkp in items:
        if blkvolbkp.lifecycle_state == 'AVAILABLE':

        # print(blkvolbkp.display_name)
        # print(blkvolbkp.lifecycle_state)
        # print(blkvolbkp.unique_size_in_gbs)
        # print(blkvolbkp.source_type)
        # print(blkvolbkp.time_created.strftime('%Y-%m-%d %H:%M:%S'))
        # print(blkvolbkp.type)

            my_blk_backups.append(blkvolbkp)
    return my_blk_backups