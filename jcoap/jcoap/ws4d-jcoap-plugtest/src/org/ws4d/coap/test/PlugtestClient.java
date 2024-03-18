package org.ws4d.coap.test;

import java.net.InetAddress;
import java.net.UnknownHostException;
import org.ws4d.coap.core.CoapClient;
import org.ws4d.coap.core.CoapConstants;
import org.ws4d.coap.core.connection.BasicCoapChannelManager;
import org.ws4d.coap.core.connection.api.CoapChannelManager;
import org.ws4d.coap.core.connection.api.CoapClientChannel;
import org.ws4d.coap.core.enumerations.CoapMediaType;
import org.ws4d.coap.core.enumerations.CoapRequestCode;
import org.ws4d.coap.core.messages.api.CoapRequest;
import org.ws4d.coap.core.messages.api.CoapResponse;
import org.ws4d.coap.core.rest.CoapData;

/**
 * Client Application for Plugtest 2012, Paris, France Execute with argument
 * Identifier (e.g., TD_COAP_CORE_01)
 *
 * @author Nico Laum
 * @author Christian Lerche
 */
public class PlugtestClient implements CoapClient {

	private CoapChannelManager channelManager = null;
	private CoapClientChannel clientChannel = null;
	private CoapRequest request = null;
	private String ip = null;
	private int port = 0;

	public static void main(String[] args) {
		PlugtestClient client = new PlugtestClient();
		client.start("127.0.0.1", CoapConstants.COAP_DEFAULT_PORT, "TD_COAP_LINK_02", "");
	}

	public void start(String serverAddress, int serverPort, String testcase, String filter) {

		this.ip = serverAddress;
		this.port = serverPort;

		init(CoapRequestCode.GET, "/.well-known/core", false);
		System.out.println("QueryPath: " + this.request.getUriPath());

		// reliable GET
		if (testcase.equals("TD_COAP_CORE_01")) {
			init(CoapRequestCode.GET, "/test", true);

			// reliable POST
		} else if (testcase.equals("TD_COAP_CORE_02")) {
			init(CoapRequestCode.POST, "/test", true);
			this.request.setPayload(new CoapData("Content of new resource /test", CoapMediaType.text_plain));

			// reliable PUT
		} else if (testcase.equals("TD_COAP_CORE_03")) {
			init(CoapRequestCode.PUT, "/test", true);
			this.request.setPayload(new CoapData("Content of new resource /test", CoapMediaType.text_plain));

			// reliable DELETE
		} else if (testcase.equals("TD_COAP_CORE_04")) {
			init(CoapRequestCode.DELETE, "/test", true);

			// UNreliable GET
		} else if (testcase.equals("TD_COAP_CORE_05")) {
			init(CoapRequestCode.GET, "/test", false);

			// UNreliable POST
		} else if (testcase.equals("TD_COAP_CORE_06")) {
			init(CoapRequestCode.POST, "/test", false);
			this.request.setPayload(new CoapData("Content of new resource /test", CoapMediaType.text_plain));

			// UNreliable PUT
		} else if (testcase.equals("TD_COAP_CORE_07")) {
			init(CoapRequestCode.PUT, "/test", false);
			this.request.setPayload(new CoapData("Content of new resource /test", CoapMediaType.text_plain));

			// UNreliable DELETE
		} else if (testcase.equals("TD_COAP_CORE_08")) {
			init(CoapRequestCode.DELETE, "/test", false);

		} else if (testcase.equals("TD_COAP_CORE_09")) {
			init(CoapRequestCode.GET, "/separate", true);

		} else if (testcase.equals("TD_COAP_CORE_10")) {
			init(CoapRequestCode.GET, "/test", true);
			this.request.setToken("AABBCCDD".getBytes());

		} else if (testcase.equals("TD_COAP_CORE_11")) {
			init(CoapRequestCode.GET, "/test", true);

		} else if (testcase.equals("TD_COAP_CORE_12")) {
			init(CoapRequestCode.GET, "/seg1/seg2/seg3", true);

		} else if (testcase.equals("TD_COAP_CORE_13")) {
			init(CoapRequestCode.GET, "/query", true);
			this.request.setUriQuery("first=1&second=2&third=3");

		} else if (testcase.equals("TD_COAP_CORE_14")) {
			init(CoapRequestCode.GET, "/test", true);

		} else if (testcase.equals("TD_COAP_CORE_15")) {
			init(CoapRequestCode.GET, "/separate", true);

		} else if (testcase.equals("TD_COAP_CORE_16")) { // jcoap-draft18/ws4d-jcoap-plugtest/src/org/ws4d/coap/test
			init(CoapRequestCode.GET, "/separate", false);

		} else if (testcase.equals("TD_COAP_LINK_01")) {
			init(CoapRequestCode.GET, "/.well-known/core", false);

		} else if (testcase.equals("TD_COAP_LINK_02")) {
			init(CoapRequestCode.GET, "/.well-known/core", false);
			this.request.setUriQuery("rt=" + filter);
		} else {
			System.out.println("===Failure=== (unknown test case)");
			System.exit(-1);
		}
		run();
	}

	public void init(CoapRequestCode requestCode, String path, boolean reliable) {
		this.channelManager = BasicCoapChannelManager.getInstance();
		this.channelManager.setMessageId(1000);

		try {
			this.clientChannel = this.channelManager.connect(this, InetAddress.getByName(this.ip), this.port);
			if (this.clientChannel == null) {
				System.out.println("Connect failed.");
				System.exit(-1);
			}
			this.request = this.clientChannel.createRequest(requestCode, path, reliable);

		} catch (UnknownHostException e) {
			e.printStackTrace();
			System.exit(-1);
		}
	}

	public void run() {
		if (this.request.getPayload() != null) {
			System.out.println(
					"Send Request: " + this.request.toString() + " (" + new String(this.request.getPayload()) + ")");
		} else {
			System.out.println("Send Request: " + this.request.toString());
		}
		this.clientChannel.sendMessage(this.request);
	}

	@Override
	public void onConnectionFailed(CoapClientChannel channel, boolean notReachable, boolean resetByServer) {
		System.out.println("Connection Failed");
		System.exit(-1);
	}

	@Override
	public void onResponse(CoapClientChannel channel, CoapResponse response) {
		if (response.getPayload() != null) {
			System.out.println("Response: " + response.toString() + " (" + new String(response.getPayload()) + ")");
		} else {
			System.out.println("Response: " + response.toString());
		}
	}

	@Override
	public void onMCResponse(CoapClientChannel channel, CoapResponse response, InetAddress srcAddress, int srcPort) {
		System.out.println("Received Multicast Response");
	}
}