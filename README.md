## Change a Public IP for an OCI instance

This Python function will help you to change the public IP of a specific compute instance, given its OCID.

### Prerequisites
1. Define the policy that gives privileges to "any-user" to manage vNICs resources in the desired compartment or tenancy (with the required condition).
```
Allow any-user to manage virtual-network-family in compartment <compartment-name> where ALL {request.principal.type= 'fnfunc', request.resource.compartment.id = '<compartment-ocid>'}
```
2. Define the policy that gives privileges to "any-user" to use instances resources in the desired compartment or tenancy (with the required condition).
```
Allow any-user to use instance-family in compartment <compartment-name> where ALL {request.principal.type= 'fnfunc', request.resource.compartment.id = '<compartment-ocid>'}
```
3. The instance to be updated must have a Reserved Public IP.

Once you've created the required IAM policies, you can go to create a new python function using the Fn Project CLI. Then you can replace the content for each one of the files with the code in this repo :)

Finally, in order to test the function you can type the following to invoke it.
```
echo '{"instance_id": "ocid1.instance.oc1.phx.anyhql..........vv5jzicyq"}' | fn invoke app-general-purpose change-ip-python
```

