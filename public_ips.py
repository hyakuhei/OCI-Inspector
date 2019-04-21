# Listing public IP's requires:
# scope: AVAILABILITY_DOMAIN|REGION
# availability-domain $id
# compartment-id

# Map all Compartments
# Pull back all compute instances in compartments and yank their AD
# That should be all required to get IPs

import oci

from anytree import Node, RenderTree

config = oci.config.from_file("~/.oci/config", "DEFAULT")
identity = oci.identity.IdentityClient(config)
compute = oci.core.ComputeClient(config)
vcnclient = oci.core.VirtualNetworkClient(config)
user = identity.get_user(config["user"]).data

# Take a security list response object and format it into a single line
def format_security_list_rule(rule,direction):
    "ALLOW IN:  TCP 22,22 FROM 0.0.0.0 to 0.0.0.0"
    "ALLOW OUT: TCP 443,4435 FROM 0.0.0.0 to 0.0.2.1"
    # 6 = TCP
    # 17 = UDP
    
    

# Warning - here be recursion and nested loops - yay.
def walk_compartments(parentNode, compartment):
    thisNode = None
    if parentNode == None: 
        #We are the root
        thisNode = Node(compartment.name, classification="COMPARTMENT", oci_object=compartment)
    else:
        thisNode = Node(compartment.name, classification="COMPARTMENT", oci_object=compartment, parent=parentNode)

    vcns = oci.pagination.list_call_get_all_results(
        vcnclient.list_vcns,
        compartment.id,
    ).data
    for vcn in vcns:
        vcnNode = Node(vcn.display_name, classification="VCN", oci_object=vcn, parent=thisNode)
        security_lists = oci.pagination.list_call_get_all_results(
            vcnclient.list_security_lists,
            compartment.id,
            vcn.id
        ).data
        for seclist in security_lists:
            seclistNode = Node(seclist.display_name, classification="SEC LIST", oci_object=seclist, parent=vcnNode)
            for ingress in seclist.ingress_security_rules:
                statefullness = "STATEFUL" if ingress.is_stateless == False else "STATELESS"
                ports = ""
                if tcp_options != None:

                "{}: [{}] {} {}"
                _ = Node()


    compute_instances = oci.pagination.list_call_get_all_results(
        compute.list_instances,
        compartment.id
    ).data
    for instance in compute_instances:
        ciNode = Node(instance.display_name, classification="INSTANCE", oci_object=instance, parent=thisNode)
        attached_vnics = oci.pagination.list_call_get_all_results(
            compute.list_vnic_attachments,
            compartment.id,
            instance_id=instance.id
        ).data
        for attached in attached_vnics:
            vnic = vcnclient.get_vnic(attached.vnic_id).data
            _ = Node(vnic.public_ip, classification="PUBLIC IP", oci_object=vnic, parent=ciNode)
            _ = Node(vnic.private_ip, classification="PRIVATE IP", oci_object=vnic, parent=ciNode)
            
    child_compartments = oci.pagination.list_call_get_all_results(
        identity.list_compartments, 
        compartment.id,
        access_level="ACCESSIBLE"
    ).data
    if len(child_compartments) == 0:
        return thisNode
    else:
        for compartment in child_compartments:
            walk_compartments(thisNode,compartment)
    
    return thisNode #This return is basically ignored apart from the very top level return of the root

#print("User {} has root compartment of {}".format(user.description, user.compartment_id))
root_comp = identity.get_compartment(user.compartment_id)
tree = walk_compartments(None, root_comp.data)

for pre, _, node in RenderTree(tree):
    print("{}{}{}   {}".format(pre, "[{}]: ".format(node.classification), node.name, node.oci_object.id))

#print(RenderTree(tree))

