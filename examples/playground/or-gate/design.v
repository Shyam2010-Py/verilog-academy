`default_nettype none
`timescale 1ns / 1ps

// A two-input OR gate. The output is low only when both inputs are low.
module or_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a | b;

endmodule

`default_nettype wire
