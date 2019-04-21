Note:
* This is a note, it's a thing to be read
! This is a cautionary note it's a thing to read and keep in mind

Prequisites:
* Install homebrew to make life suck less
* Install jq under brew so that you can easily manage json on the command line
* Install the OCI CLI

```bash
export ROOT_COMP_OCID=ocid1.compartment.oc1..aaaaaaaaf6yd7lzctqkacbph4om6frvjfcrf2dtyjba44glk5mn5gxvc2cra
export APPROOT_COMP_OCID=ocid1.compartment.oc1..aaaaaaaaf4pm5pft4fss6wdh3ozkbeldgfk6tys4bh325fupl743rptpqm2a
export HW_DEV_COMP_OCID=ocid1.compartment.oc1..aaaaaaaaa2jx4d6mlv6fwelmsbaxrdcrh4vvbvl4l43pj6rvq3ip7ako562q
export HW_NET_COMP_OCID=ocid1.compartment.oc1..aaaaaaaapzo4ckgk2zjmhxbgwwnztwa572luhubzd74e6won6b4wjqunvk3q
export HW_DB_COMP_OCID=ocid1.compartment.oc1..aaaaaaaa7ocsymsey4sq37qxeavrmf6o4atau5jnsx7kcb55rm5rkxbcd67a
```

The architecture has a bastion node running in the NET compartment, we called it Bastino - lets find it's OCID so we can go hunting for it's IP address
* This runs instance list in the network compartment, identifies the instance by the name "Bastino" and print's that instance's ID. The tr command strips the "" from the output
! Note this does not play nicely with paginated output
```bash
export BASTINO=$(oci compute instance list --compartment-id $HW_NET_COMP_OCID --lifecycle-state RUNNING | jq '.data[] | if ."display-name" == "Bastino" then .id else "" end' | tr -d '"')
``` 

Lets grab the OCID of the VNIC that is in use:
```bash
export HW_NET_VNC_OCID=$(oci network vcn list -c $HW_NET_COMP_OCID | jq '.data[]."id"' | tr -d '"')
```

The subnet that the bastion resides within is called "hw_lb_subnet" so fetch the OCID for that under this VNC
```bash
export HW_LB_SUBNET_OCID=$(oci network subnet list -c $HW_NET_COMP_OCID --vcn-id $HW_NET_VNC_OCID | jq '.data[] | select(."display-name" == "hw_lb_subnet") | .id' | tr -d '"')
```

Get the VNIC-ID of the Private IP attached to Bastino:
```bash
export HW_BASTINO_VNIC_OCID=$(oci network private-ip list --all --subnet-id $HW_LB_SUBNET_OCID | jq '.data[] | select(."display-name" == "Bastino") | .id | tr -d '"')
```
### Find the public IP of my instance <COMP> in <COMPARTMENT>
* Set the Compartment ID
* Pull back all instances in that Compartment
* Look up public-ip from compartment and instance ID

```bash
export HW_NET_COMP_OCID=ocid1.compartment.oc1..aaaaaaaapzo4ckgk2zjmhxbgwwnztwa572luhubzd74e6won6b4wjqunvk3q
IFS='|' read BASTINO_AD BASTINO_ID <<< "$(oci compute instance list --compartment-id $HW_NET_COMP_OCID | jq '.data[] | select(."display-name" == "Bastino") | ."availability-domain" + "|" + .id' | tr -d '"')" && IFS=' '
oci network public-ip list --scope AVAILABILITY_DOMAIN --compartment-id $HW_NET_COMP_OCID --availability-domain $BASTINO_AD | jq '.data[] | ."ip-address"'
```

* Print the IP for Bastino:
```bash
oci network public-ip list --scope AVAILABILITY_DOMAIN --compartment-id $HW_NET_COMP_OCID --availability-domain $BASTINO_AD | jq '.data[] | ."ip-address"' | tr -d '"'
```

### Snippets
Print the subnet name, cidr range and OCID within a specific VCN and compartment
```bash
oci network subnet list -c $HW_NET_COMP_OCID --vcn-id $HW_NET_VNC_OCID | jq '.data[] | ."display-name" + " " + ."cidr-block" + " " + ."id"'
```
