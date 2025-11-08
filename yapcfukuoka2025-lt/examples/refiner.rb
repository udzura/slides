module StringAddressViewable
  refine String do
    def inspect
      super
    end
  end
end

def dump_string_address(str)
  Module.new do
    using StringAddressViewable
    puts str.inspect
  end
end

str = "Hello YAPC"
dump_string_address(str)
pp str

class String
  alias original_inspect inspect
  def inspect
    super
  end
  alias inspect_with_address inspect
  alias inspect original_inspect
end
