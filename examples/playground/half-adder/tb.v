`default_nettype none
`timescale 1ns / 1ps

module half_adder_tb;
    reg  a;
    reg  b;
    wire sum;
    wire carry;
    reg [1:0] vec;
    integer i;
    integer errors;
    integer a_int;
    integer b_int;

    half_adder dut (.a(a), .b(b), .sum(sum), .carry(carry));

    initial begin
        errors = 0;
        $display("Half adder truth table");
        $display("a b | sum carry | a+b");
        $display("----+-----------+----");
        for (i = 0; i < 4; i = i + 1) begin
            vec = i;
            {a, b} = vec;
            #1;
            a_int = a;
            b_int = b;
            $display("%b %b |  %b    %b   |  %0d", a, b, sum, carry, a_int + b_int);
            if (sum !== (a ^ b)) errors = errors + 1;
            if (carry !== (a & b)) errors = errors + 1;
        end
        if (errors == 0) $display("PASS: 4/4 rows match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
