/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

/*
 * Defining the headers for padding
*/

header padding_1024 {
    bit<8192> pad_1024; 
}

header padding_512 {
    bit<4096> pad_512; 
}

header padding_256 {
    bit<2048> pad_256; 
}

header padding_128 {
    bit<1024> pad_128; 
}

header padding_64 {
    bit<512> pad_64; 
}

header padding_32 {
    bit<256> pad_32; 
}

header padding_16 {
    bit<128> pad_16; 
}

header padding_8 {
    bit<64> pad_8; 
}

header padding_4 {
    bit<32> pad_4; 
}

header padding_2 {
    bit<16> pad_2; 
}

header padding_1 {
    bit<8> pad_1; 
}

struct info_t {
    bit<8> rand_value;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata {
    
    info_t info;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    udp_t		 udp;
    /*stats_t      interarr;*/
    padding_256  padd_256;
    padding_128  padd_128;
    padding_64   padd_64;
    padding_32   padd_32;
    padding_16   padd_16;
    padding_8   padd_8;
    padding_4   padd_4;
    padding_2   padd_2;
    padding_1   padd_1;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

	state start {
		transition parse_ethernet;
	}

	state parse_ethernet {
		packet.extract(hdr.ethernet);
		transition parse_ipv4;
	}	

	state parse_ipv4 {
		packet.extract(hdr.ipv4);
		transition parse_udp;
	}

    state parse_udp {
		packet.extract(hdr.udp);
		transition accept;
	}

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    /*Define the packet size to pad the packets to*/
    bit<32> padTo = 512;
    bit<32> packetLength = standard_metadata.packet_length;
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(egressSpec_t port) {
		  standard_metadata.egress_spec = port;
    }

    table ipv4_firewall {
      key = {
        hdr.ethernet.srcAddr : exact;
        hdr.ethernet.dstAddr : exact;
        hdr.ipv4.srcAddr : exact;
        hdr.ipv4.dstAddr : exact;
      }

      actions = {
        drop;
      }

      size = 16;
    }

    table ipv4_lpm {
  		key = {
        hdr.ethernet.dstAddr : exact;
  			hdr.ipv4.dstAddr : exact;
  		}

  		actions = {
  			drop;
  			ipv4_forward;
  		}

  		size = 16;
    }

    apply {
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
            ipv4_firewall.apply();
        }
	/* add the padding */
        if ((packetLength+256)<=padTo) {
 		hdr.padd_256.setValid();
		packetLength = packetLength+256;
	}
	if ((packetLength+128)<=padTo) {
 		hdr.padd_128.setValid();
		packetLength = packetLength+128;
	}
	if ((packetLength+64)<=padTo) {
 		hdr.padd_64.setValid();
		packetLength = packetLength+64;
	}
	if ((packetLength+32)<=padTo) {
 		hdr.padd_32.setValid();
		packetLength = packetLength+32;
	}
	if ((packetLength+16)<=padTo) {
 		hdr.padd_16.setValid();
		packetLength = packetLength+16;
	}
	if ((packetLength+8)<=padTo) {
 		hdr.padd_8.setValid();
		packetLength = packetLength+8;
	}
	if ((packetLength+4)<=padTo) {
 		hdr.padd_4.setValid();
		packetLength = packetLength+4;
	}
	if ((packetLength+2)<=padTo) {
 		hdr.padd_2.setValid();
		packetLength = packetLength+2;
	}
	if ((packetLength+1)<=padTo) {
 		hdr.padd_1.setValid();
		packetLength = packetLength+1;
	}

  /* Add digest here */
  random(meta.info.rand_value,(bit<8>) 0, (bit<8>) 255);
  meta.info.srcAddr = hdr.ipv4.srcAddr;
  meta.info.dstAddr = hdr.ipv4.dstAddr;
  digest(1, meta.info);
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
		packet.emit(hdr.ethernet);
		packet.emit(hdr.ipv4);
		packet.emit(hdr.udp);
    		packet.emit(hdr.padd_256);
		packet.emit(hdr.padd_128);
		packet.emit(hdr.padd_64);
		packet.emit(hdr.padd_32);
		packet.emit(hdr.padd_16);
		packet.emit(hdr.padd_8);
		packet.emit(hdr.padd_4);
		packet.emit(hdr.padd_2);
		packet.emit(hdr.padd_1);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
