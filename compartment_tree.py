import oci

from anytree import Node, RenderTree

config = oci.config.from_file("~/.oci/config", "DEFAULT")
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data

def walk_compartments(parentNode, compartment):
    thisNode = None
    if parentNode == None: 
        #We are the root
        thisNode = Node(compartment.name, oci_object=compartment)
    else:
        thisNode = Node(compartment.name, oci_object=compartment, parent=parentNode)

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

root_comp = identity.get_compartment(user.compartment_id)
tree = walk_compartments(None, root_comp.data)

for pre, _, node in RenderTree(tree):
    print("{}{}  {}".format(pre, node.name, node.oci_object.id))

#print(RenderTree(tree))