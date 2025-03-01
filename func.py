import io
import json
import logging
import oci

from fdk import response

def handler(ctx, data: io.BytesIO = None):
    
    try:
        message = "No OCID  ->  "

        # Read input
        body = json.loads(data.getvalue()) if data else {}
        instance_ocid = body.get("instance_id")

        if not instance_ocid:
            message += "Instance OCID is required  ->  "

        # Load OCI config
        signer = oci.auth.signers.get_resource_principals_signer()
        compute_client = oci.core.ComputeClient(config={}, signer=signer)
        vnic_client = oci.core.VirtualNetworkClient(config={}, signer=signer)

        # Get instance details
        instance = compute_client.get_instance(instance_ocid).data
        vnics = compute_client.list_vnic_attachments(instance.compartment_id, instance_id=instance_ocid).data

        if not vnics:
            message += "No VNICs found for instance.  ->  "

        vnic_id = vnics[0].vnic_id  # Assume first VNIC
        vnic = vnic_client.get_vnic(vnic_id).data
        
        if not vnic.public_ip:
            message += "Instance does not have a public IP.  ->  "

        old_ip = vnic.public_ip

        # Get current Private IP details
        private_ip_list = vnic_client.list_private_ips(vnic_id=vnic_id).data

        for private_ip in private_ip_list:
            if private_ip.ip_address == vnic.private_ip:
                private_ip_ocid = private_ip.id
                break
        else:
            message += "  ....  Private IP not found.  ->  "

        # Get current Public IP details
        public_ip_list = vnic_client.list_public_ips(scope="REGION", compartment_id=instance.compartment_id).data

        for public_ip in public_ip_list:
            if public_ip.ip_address == old_ip:
                public_ip_ocid = public_ip.id
                break
        else:
            message += "  ....  Public IP not found.  ->  "

        # Unassign current public IP
        vnic_client.delete_public_ip(public_ip_id=public_ip_ocid)

        message += "  ->  Elimino la IP!!  ->  "        

        # Assign new public IP
        new_ip = vnic_client.create_public_ip(
            oci.core.models.CreatePublicIpDetails(
                compartment_id=instance.compartment_id,
                display_name="NewPublicIP_" + instance.display_name,
                lifetime="RESERVED",
                freeform_tags={"IP":"Primary"},
                private_ip_id=private_ip_ocid
            )
        ).data.ip_address

        message += "  ->  Se asigno nueva IP!!  ->  "
        message += "  ->  Public IP changed successfully => " + "old_ip: " + old_ip + " and new_ip: " + new_ip
        #message += "  ->  VNIC_PRVT_IP: " + vnic.private_ip

    except (Exception, ValueError) as ex:
        logging.getLogger().info('Exception Error!: ' + str(ex))
        message += "Exception Error!: " + str(ex)

    logging.getLogger().info("Inside Python ChangeIP function")
    return response.Response(
        ctx, response_data=json.dumps(
            {"message": "{0}".format(message)}),
        headers={"Content-Type": "application/json"}
    )
