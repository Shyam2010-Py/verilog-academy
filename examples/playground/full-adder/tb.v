`default_nettype none
`timescale 1ns / 1ps

module full_adder_tb;
    reg  a;
    reg  b;
    reg  cin;
    wire sum;
    wire carry;
    reg [2:0] vec;
    integer i;
    integer errors;
    integer a_int;
    integer b_int;
    integer cin_int;

    full_adder dut (.a(a), .b(b), .cin(cin), .sum(sum), .carry(carry));

    initial begin
        errors = 0;
        $display("Full adder truth table");
        $display("a b cin | sum carry | a+b+cin");
        $display("--------+-----------+--------");
        for (i = 0; i < 8; i = i + 1) begin
            vec = i;
            {a, b, cin} = vec;
            #1;
            a_int = a;
            b_int = b;
            cin_int = cin;
            $display("%b %b  %b  |  %b    %b   |    %0d", a, b, cin, sum, carry, a_int + b_int + cin_int);
            if (sum !== (a ^ b ^ cin)) errors = errors + 1;
            if (carry !== ((a & b) | (cin & (a ^ b)))) errors = errors + 1;
        end
        if (errors == 0) $display("PASS: 8/8 rows match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
