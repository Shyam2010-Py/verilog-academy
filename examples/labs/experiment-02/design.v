`default_nettype none
`timescale 1ns / 1ps

// EC-410 Experiment 02 - half adder and full adder.
// Both modules are combinational and use dataflow assignments only.

module half_adder (
    input  wire a,
    input  wire b,
    output wire sum,
    output wire carry
);

    assign sum   = a ^ b;
    assign carry = a & b;

endmodule


module full_adder (
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire carry
);

    wire p;   // a XOR b: the propagate term
    wire g;   // a AND b: the generate term
    wire pc;  // propagate AND carry-in

    assign p     = a ^ b;
    assign g     = a & b;
    assign sum   = p ^ cin;
    assign pc    = p & cin;
    assign carry = g | pc;

endmodule

`default_nettype wire
