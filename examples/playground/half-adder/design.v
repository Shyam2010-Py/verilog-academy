`default_nettype none
`timescale 1ns / 1ps

// Half adder: sum is XOR, carry is the AND of the two input bits.
module half_adder (
    input  wire a,
    input  wire b,
    output wire sum,
    output wire carry
);

    assign sum   = a ^ b;
    assign carry = a & b;

endmodule

`default_nettype wire
