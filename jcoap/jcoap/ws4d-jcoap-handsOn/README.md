# Tutorial for jCoAP Hands-on

In this tutorial we will explain how to develop a simple message exchange between devices using jCoAP.  
Furthermore, we will introduce the observe mechanism.

The following points will be covered by this tutorial:

1. Installation of Copper plugin for Mozilla Firefox
2. Introduction of jCoAP
3. Import of prepared project into Eclipse
4. Task 1: Implementation of client/server and enable simple message exchange
5. Task 2: Implementation of an air conditioner control by using the CoAP-observe mechanism

## 1. Requirements for this tutorial
* Java SE JDK 1.6+
* Eclipse IDE for Java development
* Prepared [Java project files for Hands-on](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/tree/master/ws4d-jcoap-handsOn)

## 2. Installation of the Copper Plugin for Mozilla Firefox

- [https://addons.mozilla.org/de/firefox/addon/copper-270430/](https://addons.mozilla.org/de/firefox/addon/copper-270430/)
- Click on `add to Firefox` and Confirm Installation
- Restart Firefox

After the installation you can enter anything like `coap://host:port/resourcePath/?query=filter` in the address bar.  
Copper will allow you to make any CoAP interaction.

![Copper Screenshot](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/raw/master/ws4d-jcoap-handsOn/img/CopperScreenshot.jpg)

## 3. Introduction of jCoAP
- WS4D-jCoAP: Java implementation of CoAP
 - [http://ws4d.org/](http://ws4d.org/)
 - [https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap)

#### Client Side
![Client Side  UML Diagram](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/raw/master/ws4d-jcoap-handsOn/img/Client%20UML.jpg)

**CoapClient:**  Interface that must be implemented by a client  
**Client:**  Customized implementation of a client application, implements `CoapClient`  
**Channel:**  A channel represents a connection between a Client and a Server  
**ChannelManager:**  Manages `Channels` (Timeouts, Matching Requests and Responses)  


#### Server Side
![Server Side  UML Diagram](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/raw/master/ws4d-jcoap-handsOn/img/ServerUML.jpg)

**CoapResource:**  Interface that must be supported by each resource.  
**BasicCoapResource:**  Already implemented resource with basic functionality, implements `CoapResource`  
**TemperatureResource:**  Example of a customized resource, inherits from `BasicCoapResource`  
**CoapServer:**  Interface that must be supported by a resource server  
**CoapResourceServer:**  Manages a list of resources, enables access of these resources from outside, implements `CoapServer`  
**Server:** Example of a customized implementation of a server application, creates `CoapResourceServer` and `CoapResources`  

## 4. Import of prepared project into Eclipse

You can find the required files in our repository at [https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/tree/master/ws4d-jcoap-handsOn](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/tree/master/ws4d-jcoap-handsOn)

1. *[File &raquo; Import]*
2. *[General &raquo; Existing Projects into Workspace]*
3. Browse <Project Folder>
4. Finish

* We have prepared some FIXME and TODO annotations:
 * Just open the „Task“ view
 * FIXMEs are for the first task (message exchange)
 * TODOs are for the second task (observe and AC control)
* If you do not have a „Task“ view:
 * *[Window &raquo; Show View &raquo; Other]*
 * Type `task`
 * Select *[General &raquo; Task]* view

## 5. Task 1: Implementation of client/server and enable simple message exchange

### Sequence Diagram
![Task 1 – Sequence Diagram](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/raw/master/ws4d-jcoap-handsOn/img/Task1Sequence.png)  

### Server
1. Create a new resource class TemperatureResource (already done in our example Server)
2. Instantiate a new ResourceServer
3. Instantiate a new TemperatureResource
4. Add the TemperatureResource to the ResourceServer
5. Start the ResourceServer
6. Test

#### 1. Create a new resource class TemperatureResource (TemperatureResource.java):
* We could have used the predefined `BasicCoapResource`
* `BasicCoapResource` is a resource that just keeps a static `byte[]` which is:
 * returned on GET requests
 * replaced by the payload on PUT requests
 * appended with the payload on POST requests
 * deleted on DELETE requests
 * We do not want a static `byte[]`
* Instead we want a random number to be returned on a GET
* PUT, POST and DELETE are not used
* ->So we implemented `TemperatureResource` which extends `BasicCoapResource` with:
 * A constructor to initialize the resource and disallow POST, PUT and DELETE requests and
 * Two get() methods:
 
```java
	CoapData get(List<CoapMediaType> mediaTypesAccepted);
	CoapData get(List<String> query, List<CoapMediaType> mediaTypesAccepted);
```

#### 2. Instantiate a new ResourceServer (Server.java, FIXME 1.1):
* Need a CoapResourceServer to maintain resources

```java
	CoapResourceServer resourceServer = new CoapResourceServer();
```

#### 3. Instantiate a new TemperatureResource (Server.java, FIXME 1.2):
* Resources are created like normal objects

```java
	CoapResource resource = new CoapResource();
```

#### 4. Add the TemperatureResource to the ResourceServer (Server.java, FIXME 1.3):

```java
	resourceServer.createResource(resource);
```

#### 5. Start the ResourceServer (Server.java  FIXME 1.4):

```java
	resourceServer.start(port);
	resourceServer.start(); // equals port = CoapConstants.COAP_DEFAULT_PORT
```

#### 6. Test:
* Run Server: Click on *[Run &raquo; Run]* in the Menu bar
* To stop the server, press the red terminate button in the console/task area
* Test it with Copper: `coap://127.0.0.1`
* Stretch goal:
 * Create another resource type e.g.: humidity or current time, use real sensor values if possible
 * Tip: make a copy of `TemperatureResource.java`

### Client
1. Establish a connection to the Server using the ChannelManager
2. Create a CoapRequest & add some Options
3. Send the CoapRequest
4. Wait for CoapResponse & Print the CoapResponse on the console (already done in our example)
5. Test

#### 1. Establish a connection to the Server using the ChannelManager (Client.java, FIXME 2.1 & 2.2):
* A client must implement CoapClient interface

```java
	public class Client implements CoapClient {...}
```
* A CoapChannelManager is used to manage different connections and to establish a connection to a server

```java
	channelManager = BasicCoapChannelManager.getInstance();
	clientChannel = channelManager.connect(CoapClient client,InetAddress serverIP, int serverPort);
```

#### 2. Create a CoapRequest & add some Options (Client.java, FIXME 2.3 - 2.5):
* A channel represents a single connection and is used to create and send requests

```java
	Boolean reliable = false;
		CoapRequestCode reqCode = CoapRequestCode.GET;
			CoapRequest request = clientChannel.createRequest(reliable,reqCode);
				request.setUriPath("/temperature");
```

#### 3. Send the CoapRequest (Client.java, FIXME 2.6):

```java
	clientChannel.sendMessage(request);
```

#### 4. Wait for CoapResponse & Print the CoapResponse on the console:
* A client has some callbacks that are invoked, when the corresponding event occurs

```java
	public void onConnectionFailed(...);
	public void onResponse(...); // = Unicast
	public void onMCResponse(...); // MC = Multicast
```

#### 5. Test:
* Run Server: select Server.java and click on *[Run &raquo; Run]* in the Menu bar
* Run Client: select Client.java and click on *[Run &raquo; Run]* in the Menu bar
* Stretch goal:
 * If you have written your own resources before: GET them
 * GET the `/.well-known/core` resource (it is generated automatically by the server)
 * GET the `/.well-known/core` resource using multicast (aka. Multicast Discovery)
 
```java
	// Multicast addresses
	// CoapConstants.COAP_ALL_NODES_IPV4_MC_ADDR
	// CoapConstants.COAP_ALL_NODES_IPV6_LL_MC_ADDR
	// CoapConstants.COAP_ALL_NODES_IPV6_SL_MC_ADDR
	
	// On Multicast: add token to match multicast request and unicast responses
	request.setToken("MCToken".getBytes());
```


## 6. Task 2: Implementation of a AC control by using the CoAP-observe mechanism
1. Use the eventing mechanism CoAP-Observe  
2. Let the server notify clients every 5 seconds about a changed TemperatureResource  
3. Implement an Air Conditioner Resource with the path `/ACControl`, that can be set to `high`, `medium`, `low` or `off`  

![Task 2 - Sequence diagram](https://gitlab.amd.e-technik.uni-rostock.de/ws4d/jcoap/raw/master/ws4d-jcoap-handsOn/img/Task2Sequence.png)

### 1. Use the eventing mechanism CoAP-Observe (Server.java, TODO 3.1):
 * Mark the TemperatureResource as observable
 
```java
	resource.setObservable(true);
```
### 2. Let server notify clients every 5 s about changed TemperatureResource (Server.java, TODO 3.2):
 * indicate a change for resource every 5 seconds
 
```java
	while (true) {
		try {Thread.sleep(5000);}
		catch (InterruptedException e) {/*do nothing*/}
		resource.changed(); // Notify
	}
```
### 3. Implement an Air Conditioner Resource with the path `/ACControl`, that can be set to `high`, `medium`, `low` or `off` (Client.java & Server.java, TODO 4.1 - 5.2):
 * Change exitAfterResponse to false (Client.java, TODO 4.1)
 * Add the observe-option to your CoAP-GET request (Client.java, TODO 4.2)
 
```java
	request.setObserveOption(0);
```
 * add a BasicCoapResource to the ResourceServer (Server.java, TODO 5.1)
 
```java
	resourceServer.createResource(newBasicCoapResource("/ACControl","off",CoapMediaType.text_plain));
```
 * send PUT request (Client.java, TODO 5.2)

```java
	CoapRequest request = clientChannel.createRequest(true, CoapRequestCode.PUT);
	request.setUriPath("/ACControl");
	request.setContentType(CoapMediaType.text_plain);
``` 
Depending on the received temperature, set the payload to high, medium, low or off

```
	high	28 <=	Temperature
	medium	25 <=	Temperature < 28
	low		21 <=	Temperature < 25
	off				Temperature < 21
```


```java
	request.setPayload("medium".getBytes());
	clientChannel.sendMessage(request);
```

