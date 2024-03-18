package org.ws4d.coap.handsOn;

import org.ws4d.coap.core.CoapConstants;
import org.ws4d.coap.core.enumerations.CoapMediaType;
import org.ws4d.coap.core.rest.BasicCoapResource;
import org.ws4d.coap.core.rest.CoapResourceServer;

public class Server {

	private static Server coapServer;
    private CoapResourceServer resourceServer;
    
    public void startServer() {
		System.out.println("=== START Server ===");
    	if (this.resourceServer != null){
    		this.resourceServer.stop();
    	}
    	/* FIXME 1.1: Instantiate a new CoapResourceServer */
//    	this.resourceServer = new CoapResourceServer();
		
		/* FIXME 1.2: Instantiate a TemperatureResource */
//		TemperatureResource resource = new TemperatureResource();
		
		/* TODO 3.1: Skip for now! In the 2nd step we will make this resource observable right here */
//		resource.set<CTRL><SPACE>;
		
		/* FIXME 1.3: Add our resource to the server */
//		this.resourceServer.createResource(resource);
		
		/* TODO 5.1: Skip for now! In the 3rd step we will add another resource here*/
//		this.resourceServer.createResource( new BasicCoapResource("/ACControl","off",CoapMediaType.text_plain));

		/* this starts the server */
		try {
			/* FIXME 1.4: determine port to run */
//			this.resourceServer.start(CoapConstants.COAP_DEFAULT_PORT);
		} catch (Exception e) {
		    System.err.println(e.getLocalizedMessage());
		}
		
		/* TODO 3.2: Skip for now! In the 2nd step we will notify about a changed resource right here */
//		while(true){
//			try {Thread.sleep(5000);}
//			catch (InterruptedException e) {/*do nothing*/}
//			resource.changed(); // Notify about changed resource
//		}
    }
	
	/* *************************************************************************************************** */
	/* Last but not least the main method to get things running                                            */
	/* *************************************************************************************************** */
	
    public static void main(String[] args) {
    	coapServer = new Server();
    	coapServer.startServer();
    }
}
