# frozen_string_literal: true

require "test_helper"

class MyRustGemTest < Test::Unit::TestCase
  test "VERSION" do
    assert do
      ::MyRustGem.const_defined?(:VERSION)
    end
  end

  test "something useful" do
    assert_equal("expected", "actual")
  end
end
