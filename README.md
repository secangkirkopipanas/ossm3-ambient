# OpenShift Service Mesh 3 Onboarding

Documentation on Openshift Service Mesh 3 with Ambient mode into OpenShift cluster. We will be using **WebStore** application what contains 3 simple microservices (_written in Python 3_) to be deployed as mesh.
> to be continued

## Version details

   - **Istio**: v1.24.3
   - **IstioCNI**: v1.27.3
   - **Ztunnel**: v1.27.3


## Required operators
 
   - OpenShift Service Mesh 3 operator
   - Kiali operator
   - Red Hat build of OpenTelemetry operator
   - Cluster Observability operator


## Additional things if you want to adopt Gateway API in Amient mode to your cluster

   - [Gateway API](https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml)
      This Gateway API is required to be installed on OpenShift v4.17 and below.


## How to install

1. Install all required operators via OpenShift,

2. Install all required additional things via OC CLI,

   ```bash
   # Install Gateway API in the cluster
   oc apply -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.4.1/standard-install.yaml
   ```

3. Apply YAML manifest files:
   
   ```bash
   # Create Istio instance
   oc apply -f manifests/operator/01-ossm3/istio.yaml

   # Create IstioCNI instance
   oc apply -f manifests/operator/01-ossm3/istiocni.yaml

   # Create Ztunnel instance. This will select the node based on 'maistra.io/exclude-ztunnel=false' label
   oc apply -f manifests/operator/01-ossm3/ztunnel.yaml

   # To exclude node from hosting ztunnel, label the node with 'maistra.io/exclude-ztunnel=false'
   # oc label node <node-name> maistra.io/exclude-ztunnel=false

   # Create external gateway instance (optional)
   oc apply -f manifests/operator/01-ossm3/external-gateway.yaml
   ```

4. Wait for the process until all instances under **Red Hat OpenShift Service Mesh 3** operator are `Healthy` state.

5. Apply YAML manifest files:

   ```bash
   # Create application namespace 'webstore'
   oc apply -f manifests/app/00-prereq/

   # Deploy the Service Mesh configurations
   oc apply -f manifests/app/01-config/

   # Deploy the Microservices
   oc apply -f manifests/app/02-deps/
   ```

6. 

## How to build the application image

The following 3 applications are available:

   - Order service
   - Payment service
   - Account service

To build all application images:

```bash
./build-image.sh all
```

To build individual application image:

```bash
./build.image.sh order
```
