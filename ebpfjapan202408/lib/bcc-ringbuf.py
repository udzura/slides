#!/usr/bin/python3
import time
from bcc import BPF
prog = r"""
#include <linux/sched.h>
struct data_t {
    char comm[TASK_COMM_LEN];
};
BPF_RINGBUF_OUTPUT(buffer, 1 << 4);
int hello(struct pt_regs *ctx) {
    struct data_t data = {};
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    buffer.ringbuf_output(&data, sizeof(data), 0);
    return 0;
}
"""

b = BPF(text=src)
def callback(ctx, data, size):
    print("Hello world! comm = %s" % (b["buffer"].event(data).comm))

b['buffer'].open_ring_buffer(callback)

while 1:
    b.ring_buffer_poll()
    time.sleep(0.5)
