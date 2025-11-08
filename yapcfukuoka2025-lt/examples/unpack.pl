#!/usr/bin/perl
use strict;
use warnings;
use Socket;
use Data::Dumper;

sub parse_icmp_packet {
    my ($packet) = @_;
    
    my $ip_header_len = (unpack('C', $packet) & 0x0f) * 4;
    
    my ($ver_ihl, $tos, $tot_len, $id, $frag_off, $ttl, $protocol, $checksum, $saddr, $daddr) =
        unpack('C C n n n C C n N N', substr($packet, 0, 20));
    
    my $src_ip = inet_ntoa(pack('N', $saddr));
    my $dst_ip = inet_ntoa(pack('N', $daddr));
    
    my $icmp_packet = substr($packet, $ip_header_len);
    
    my ($type, $code, $icmp_checksum, $identifier, $sequence) =
        unpack('C C n n n', $icmp_packet);
    
    my $data = substr($icmp_packet, 8);
    
    return {
        ip => {
            version => ($ver_ihl >> 4),
            header_length => ($ver_ihl & 0x0f) * 4,
            tos => $tos,
            total_length => $tot_len,
            id => $id,
            ttl => $ttl,
            protocol => $protocol,
            src_addr => $src_ip,
            dst_addr => $dst_ip,
        },
        icmp => {
            type => $type,
            code => $code,
            checksum => sprintf("0x%04x", $icmp_checksum),
            identifier => $identifier,
            sequence => $sequence,
            data => $data,
            data_hex => unpack('H*', $data),
        }
    };
}
my $dump_file = $ARGV[0] or die "Usage: $0 <dump_file>\n";
open my $fh, '<:raw', $dump_file or die "Cannot open $dump_file: $!\n";

while (read($fh, my $packet, 1500)) {
    last unless length($packet) > 0;
    
    if (length($packet) < 28) { 
        print "Warning: Packet too small (", length($packet), " bytes), skipping...\n";
        next;
    }
    
    eval {
        my $info = parse_icmp_packet($packet);
        print Dumper $info;
    };
    if ($@) {
        print "Error parsing packet: $@\n";
    }
}

close($fh);