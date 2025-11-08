#!/usr/bin/perl
use strict;
use warnings;
use Socket;
use Data::Dumper;
use Time::HiRes qw(time);

# ICMPプロトコル番号
use constant ICMP_ECHO_REPLY => 0;
use constant ICMP_ECHO_REQUEST => 8;

sub create_icmp_packet {
    my ($seq) = @_;
    my $type = ICMP_ECHO_REQUEST;
    my $code = 0;
    my $checksum = 0;
    my $identifier = $$;  # プロセスIDを識別子として使用
    my $data = "PerlPing" x 4;  # データ部分
    
    # チェックサムなしでパケットを作成
    my $packet = pack('C2 n3 A*', $type, $code, $checksum, $identifier, $seq, $data);
    
    # チェックサムを計算
    $checksum = calculate_checksum($packet);
    
    # チェックサムを含めて再作成
    $packet = pack('C2 n3 A*', $type, $code, $checksum, $identifier, $seq, $data);
    
    return $packet;
}

sub calculate_checksum {
    my ($msg) = @_;
    my $len = length($msg);
    my $num_shorts = int($len / 2);
    my $checksum = 0;
    
    foreach my $short (unpack("n$num_shorts", $msg)) {
        $checksum += $short;
    }
    
    # 奇数バイトの場合、最後のバイトを追加
    if ($len % 2) {
        $checksum += unpack('C', substr($msg, -1)) << 8;
    }
    
    # オーバーフローを折り返す
    $checksum = ($checksum >> 16) + ($checksum & 0xffff);
    $checksum += ($checksum >> 16);
    
    return ~$checksum & 0xffff;
}

sub parse_icmp_packet {
    my ($packet) = @_;
    
    # IPヘッダーのサイズを計算（最初の4ビットがバージョン、次の4ビットがヘッダー長）
    my $ip_header_len = (unpack('C', $packet) & 0x0f) * 4;
    
    # IPヘッダーを解析
    my ($ver_ihl, $tos, $tot_len, $id, $frag_off, $ttl, $protocol, $checksum, $saddr, $daddr) =
        unpack('C C n n n C C n N N', substr($packet, 0, 20));
    
    my $src_ip = inet_ntoa(pack('N', $saddr));
    my $dst_ip = inet_ntoa(pack('N', $daddr));
    
    # ICMPパケットを取得
    my $icmp_packet = substr($packet, $ip_header_len);
    
    # ICMPヘッダーを解析
    my ($type, $code, $icmp_checksum, $identifier, $sequence) =
        unpack('C C n n n', $icmp_packet);
    
    # データ部分を取得
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

sub get_icmp_type_name {
    my ($type) = @_;
    my %types = (
        0 => 'Echo Reply',
        3 => 'Destination Unreachable',
        4 => 'Source Quench',
        5 => 'Redirect',
        8 => 'Echo Request',
        11 => 'Time Exceeded',
        12 => 'Parameter Problem',
        13 => 'Timestamp Request',
        14 => 'Timestamp Reply',
    );
    return $types{$type} || "Unknown ($type)";
}

sub display_packet_info {
    my ($info) = @_;
    
    print "\n" . "="x60 . "\n";
    print "IP Header:\n";
    print "-"x60 . "\n";
    printf "  Version: %d\n", $info->{ip}{version};
    printf "  Header Length: %d bytes\n", $info->{ip}{header_length};
    printf "  Total Length: %d bytes\n", $info->{ip}{total_length};
    printf "  TTL: %d\n", $info->{ip}{ttl};
    printf "  Protocol: %d (ICMP)\n", $info->{ip}{protocol};
    printf "  Source: %s\n", $info->{ip}{src_addr};
    printf "  Destination: %s\n", $info->{ip}{dst_addr};
    
    print "\nICMP Header:\n";
    print "-"x60 . "\n";
    printf "  Type: %d (%s)\n", $info->{icmp}{type}, $info->{icmp}{type_name};
    printf "  Code: %d\n", $info->{icmp}{code};
    printf "  Checksum: %s\n", $info->{icmp}{checksum};
    printf "  Identifier: %d\n", $info->{icmp}{identifier};
    printf "  Sequence: %d\n", $info->{icmp}{sequence};
    printf "  Data: %s\n", $info->{icmp}{data};
    printf "  Data (hex): %s\n", $info->{icmp}{data_hex};
    print "="x60 . "\n";
}

# メイン処理
print "Ping Packet Analyzer - Dump File Reader\n\n";

my $dump_file = $ARGV[0] or die "Usage: $0 <dump_file>\n";

# ダンプファイルを開く
open(my $fh, '<:raw', $dump_file) or die "Cannot open $dump_file: $!\n";

print "Reading dump file: $dump_file\n";

my $packet_count = 0;

# ファイルからパケットデータを読み込む
while (read($fh, my $packet, 1500)) {
    last unless length($packet) > 0;
    
    $packet_count++;
    print "\n--- Packet #$packet_count ---\n";
    
    # パケットサイズが十分かチェック
    if (length($packet) < 28) {  # 最小のIP+ICMPヘッダーサイズ
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

if ($packet_count == 0) {
    print "No packets found in dump file.\n";
} else {
    print "\nTotal packets analyzed: $packet_count\n";
}

print "\nDone.\n";