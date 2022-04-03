/* -*- P4_16 -*- */
#include <core.p4>
#include "./v1model.p4"

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> CLONE_FL_1  = 2;
/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1
#define PKT_INSTANCE_TYPE_INGRESS_RECIRC 4
#define RECIRCULATE_TIMES 200
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    tos;
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

struct metadata {
    bit<32> meter_tag;
    bit<3> clone;
    bit<32> counter;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){

            TYPE_IPV4: ipv4;
            default: accept;
        }

    }

    state ipv4 {

        packet.extract(hdr.ipv4);
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
    register<bit<1>>(1) shaping;
    bit<1> tmp;

    direct_meter<bit<32>>(MeterType.packets) my_meter;

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action m_action() {
        my_meter.read(meta.meter_tag);
    }

    action cloneThis() {
        clone(CloneType.I2E, 5);
    }
    table m_read {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            m_action;
            NoAction;
        }
        default_action = NoAction;
        meters = my_meter;
        size = 16384;
    }
    table debug {
        key = {
            standard_metadata.instance_type: exact;
        }
        actions = {}
    }
    table m_filter {
        key = {
            meta.meter_tag: exact;
        }
        actions = {
            drop;
            NoAction;
        }
        default_action = drop;
        size = 16;
    }
    table apply_shaping {
        key = {
            standard_metadata.instance_type: exact;
        }
        actions = {
            drop;
            cloneThis;
            NoAction;
        }
        default_action = NoAction;
        size = 16;
    }
    action ipv4_forward(egressSpec_t port) {

        // Set the output port that we also get from the table
        standard_metadata.egress_spec = port;

        // Decrease ttl by 1
        hdr.ipv4.ttl = hdr.ipv4.ttl -1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    apply {
    	debug.apply();
        // Only if IPV4 the rule is applied. Therefore other packets will not be forwarded.
        if (hdr.ipv4.isValid()){
            ipv4_lpm.apply();
            // real packets get highest priority (7)
            if (standard_metadata.instance_type == 0){
                standard_metadata.priority = (bit<3>)7;
            }
            // dummy packets get lowest priority (0)
            else if (standard_metadata.instance_type == 1 || standard_metadata.instance_type == 4){
                standard_metadata.priority = (bit<3>)0;
            }
	    shaping.read(tmp, 0);
	    //if it has not started shaping
	    if (tmp == 0){
		cloneThis();
		shaping.write(0, 1);
	    }
	    apply_shaping.apply();
	    // Check meter
            m_read.apply();

            // Filter based on meter status
            m_filter.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    table debug {
        key = {
            standard_metadata.instance_type: exact;
        }
        actions = {}
    }
   apply {

        hdr.ipv4.tos = (bit<8>)standard_metadata.qid;
        if (standard_metadata.instance_type == PKT_INSTANCE_TYPE_INGRESS_CLONE) {
		recirculate({});
        }
   }
}


/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.tos,
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

    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
