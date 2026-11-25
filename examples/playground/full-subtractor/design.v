`default_nettype none
`timescale 1ns / 1ps

// Full subtractor: difference is three-bit parity; borrow includes bin.
module full_subtractor (
    input  wire a,
    input  wire b,
    input  wire bin,
    output wire diff,
    output wire borrow
);

    assign diff   = a ^ b ^ bin;
    assign borrow = (~a & b) | (~(a ^ b) & bin);

endmodule

`default_nettype wire
