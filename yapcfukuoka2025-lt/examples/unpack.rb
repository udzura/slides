def parse_icmp_packet(packet)
  ver_ihl = packet[0].unpack1('C')
  ip_header_len = (ver_ihl & 0x0f) * 4
  
  ip_header = packet[0, 20].unpack('C C n n n C C n N N')
  ver_ihl, tos, tot_len, id, frag_off, ttl, protocol, checksum, saddr, daddr = ip_header
  
  src_ip = IPAddr.new(saddr, Socket::AF_INET).to_s
  dst_ip = IPAddr.new(daddr, Socket::AF_INET).to_s
  
  icmp_packet = packet[ip_header_len..-1]
  
  icmp_header = icmp_packet[0, 8].unpack('C C n n n')
  type, code, icmp_checksum, identifier, sequence = icmp_header
  
  data = icmp_packet[8..-1] || ''
  
  {
    ip: {
      version: (ver_ihl >> 4),
      header_length: (ver_ihl & 0x0f) * 4,
      tos: tos,
      total_length: tot_len,
      id: id,
      ttl: ttl,
      protocol: protocol,
      src_addr: src_ip,
      dst_addr: dst_ip
    },
    icmp: {
      type: type,
      type_name: get_icmp_type_name(type),
      code: code,
      checksum: sprintf("0x%04x", icmp_checksum),
      identifier: identifier,
      sequence: sequence,
      data: data,
      data_hex: data.unpack1('H*')
    }
  }
end
