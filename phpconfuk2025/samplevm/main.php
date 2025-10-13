<?php

class VM {
    private $stack = [];
    private $instructions = [];
    private $pc = 0; // program counter

    public function load($instructions): void {
        $this->instructions = $instructions;
    }

    public function run(): void {
        while ($this->pc < count($this->instructions)) {
            $this->evaluate($this->instructions[$this->pc]);
            $this->pc++;
        }

        print("Final Stack: [" . implode(', ', $this->stack) . "]\n");
    }

    private function evaluate($instruction): void {
        list($op, $arg) = explode(' ', $instruction . ' ', 2);
        switch ($op) {
            case 'i32.const':
                $this->stack[] = (int)$arg;
                break;
            case 'i32.add':
                $b = array_pop($this->stack);
                $a = array_pop($this->stack);
                $this->stack[] = $a + $b;
                break;
            default:
                throw new Exception("Unimplemented or unsupported instruction: $op");
        }
    }
}

$vm = new VM();
$vm->load([
    'i32.const 10',
    'i32.const 20',
    'i32.add',
]);
$vm->run();