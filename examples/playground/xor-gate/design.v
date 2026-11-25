`default_nettype none
`timescale 1ns / 1ps

// XOR gives 1 when the inputs differ, so it is also a one-bit parity gate.
module xor_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a ^ b;

endmodule

`default_nettype wire
