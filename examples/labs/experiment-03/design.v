`default_nettype none
`timescale 1ns / 1ps

// EC-410 Experiment 03 - half subtractor and full subtractor.
// Borrow is asserted when the value being subtracted is larger than x.

module half_subtractor (
    input  wire x,
    input  wire y,
    output wire diff,
    output wire borrow
);

    assign diff   = x ^ y;
    assign borrow = ~x & y;

endmodule


module full_subtractor (
    input  wire x,
    input  wire y,
    input  wire bin,
    output wire diff,
    output wire borrow
);

    wire d;    // x XOR y from the first half subtractor
    wire b1;   // borrow out of the first half subtractor
    wire b2;   // borrow from subtracting bin from d

    assign d      = x ^ y;
    assign b1     = ~x & y;
    assign b2     = ~d & bin;
    assign diff   = d ^ bin;
    assign borrow = b1 | b2;

endmodule

`default_nettype wire
