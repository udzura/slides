#!/usr/bin/env ruby
require 'rbbcc'; include RbBCC
prog = "#include <linux/sched.h>
struct data_t {
    char comm[TASK_COMM_LEN];
};
BPF_RINGBUF_OUTPUT(buffer, 1 << 4);
int hello(struct pt_regs *ctx) {
    struct data_t data = {};
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    buffer.ringbuf_output(&data, sizeof(data), 0);
    return 0;
}"

b = BCC.new(text: prog).tap{|b| b.attach_kprobe(event: "sys_clone", fn_name: "hello")}
b["buffer"].open_ring_buffer do |_, data, _|
  puts "Hello world! comm = %s" % b["buffer"].event(data).comm
end
loop { b.ring_buffer_poll; sleep 0.1 }
