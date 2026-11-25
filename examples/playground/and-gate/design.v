`default_nettype none
`timescale 1ns / 1ps

// A two-input AND gate described by one continuous assignment.
module and_gate (
    input  wire a,
    input  wire b,
    output wire y
);

    assign y = a & b;

endmodule

`default_nettype wire
