`default_nettype none
`timescale 1ns / 1ps

// Half subtractor: difference is XOR; borrow is high only for 0 - 1.
module half_subtractor (
    input  wire a,
    input  wire b,
    output wire diff,
    output wire borrow
);

    assign diff   = a ^ b;
    assign borrow = (~a) & b;

endmodule

`default_nettype wire
