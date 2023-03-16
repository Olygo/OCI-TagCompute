# coding: utf-8

import oci

##########################################################################
# tag associated resources
##########################################################################


def tag_resources(type, oci_client, resource_id, freeform_tags_dict):
    
    if type == 'compute':
        details = oci.core.models.UpdateInstanceDetails(freeform_tags=freeform_tags_dict)
        response = oci_client.update_instance(resource_id,details)

    if type == 'bootvolume':
        try:
            details = oci.core.models.UpdateBootVolumeDetails(freeform_tags={})
            response = oci_client.update_boot_volume(resource_id,details)
        except:
            pass
        details = oci.core.models.UpdateBootVolumeDetails(freeform_tags=freeform_tags_dict)
        response = oci_client.update_boot_volume(resource_id,details)
        
    if type == 'volume':
        try:
            details = oci.core.models.UpdateVolumeDetails(freeform_tags={})
            response = oci_client.update_volume(resource_id,details)
        except:
            pass
        details = oci.core.models.UpdateVolumeDetails(freeform_tags=freeform_tags_dict)
        response = oci_client.update_volume(resource_id,details)

    if type == 'boot_backup':
        try:
            details = oci.core.models.UpdateBootVolumeBackupDetails(freeform_tags={})
            response = oci_client.update_boot_volume_backup(resource_id,details)
        except:
            pass
        details = oci.core.models.UpdateBootVolumeBackupDetails(freeform_tags=freeform_tags_dict)
        response = oci_client.update_boot_volume_backup(resource_id,details)

    if type == 'volume_backup':
        try:
            details = oci.core.models.UpdateVolumeBackupDetails(freeform_tags={})
            response = oci_client.update_volume_backup(resource_id,details)
        except:
            pass
        details = oci.core.models.UpdateVolumeBackupDetails(freeform_tags=freeform_tags_dict)
        response = oci_client.update_volume_backup(resource_id,details)

 
    return response

