`default_nettype none
`timescale 1ns / 1ps

// Full adder: sum is the parity of three bits; carry is the majority vote.
module full_adder (
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire carry
);

    assign sum   = a ^ b ^ cin;
    assign carry = (a & b) | (cin & (a ^ b));

endmodule

`default_nettype wire
