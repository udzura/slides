require 'benchmark/ips'

def bench(a)
  if a + 1 > 3
    true
  else
    false
  end
end

Benchmark.ips do |x|
  x.report('rand') { bench(rand(5)) }
  x.report('always_true') { bench(1) }
  x.report('always_false') { bench(3) }
end