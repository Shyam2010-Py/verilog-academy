`default_nettype none
`timescale 1ns / 1ps

module or_gate_tb;
    reg  a;
    reg  b;
    wire y;
    reg [1:0] vec;
    integer i;
    integer errors;

    or_gate dut (.a(a), .b(b), .y(y));

    initial begin
        errors = 0;
        $display("OR gate truth table");
        $display("a b | y");
        $display("----+--");
        for (i = 0; i < 4; i = i + 1) begin
            vec = i;
            {a, b} = vec;
            #1;
            $display("%b %b | %b", a, b, y);
            if (y !== (a | b)) errors = errors + 1;
        end
        if (errors == 0) $display("PASS: 4/4 rows match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
