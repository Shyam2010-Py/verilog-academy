`default_nettype none
`timescale 1ns / 1ps

module half_subtractor_tb;
    reg  a;
    reg  b;
    wire diff;
    wire borrow;
    reg [1:0] vec;
    integer i;
    integer errors;
    integer a_int;
    integer b_int;

    half_subtractor dut (.a(a), .b(b), .diff(diff), .borrow(borrow));

    initial begin
        errors = 0;
        $display("Half subtractor truth table");
        $display("a b | diff borrow | a-b");
        $display("----+-------------+----");
        for (i = 0; i < 4; i = i + 1) begin
            vec = i;
            {a, b} = vec;
            #1;
            a_int = a;
            b_int = b;
            $display("%b %b |  %b     %b    |  %0d", a, b, diff, borrow, a_int - b_int);
            if (diff !== (a ^ b)) errors = errors + 1;
            if (borrow !== ((~a) & b)) errors = errors + 1;
        end
        if (errors == 0) $display("PASS: 4/4 rows match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
