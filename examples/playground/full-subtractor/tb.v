`default_nettype none
`timescale 1ns / 1ps

module full_subtractor_tb;
    reg  a;
    reg  b;
    reg  bin;
    wire diff;
    wire borrow;
    reg [2:0] vec;
    integer i;
    integer errors;
    integer a_int;
    integer b_int;
    integer bin_int;

    full_subtractor dut (.a(a), .b(b), .bin(bin), .diff(diff), .borrow(borrow));

    initial begin
        errors = 0;
        $display("Full subtractor truth table");
        $display("a b bin | diff borrow | a-b-bin");
        $display("--------+-------------+--------");
        for (i = 0; i < 8; i = i + 1) begin
            vec = i;
            {a, b, bin} = vec;
            #1;
            a_int = a;
            b_int = b;
            bin_int = bin;
            $display("%b %b  %b  |  %b     %b    |    %0d", a, b, bin, diff, borrow, a_int - b_int - bin_int);
            if (diff !== (a ^ b ^ bin)) errors = errors + 1;
            if (borrow !== ((~a & b) | (~(a ^ b) & bin))) errors = errors + 1;
        end
        if (errors == 0) $display("PASS: 8/8 rows match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
