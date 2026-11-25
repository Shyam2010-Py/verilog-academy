`default_nettype none
`timescale 1ns / 1ps

// Positive-edge D flip-flop with active-high enable and asynchronous reset.
module d_flip_flop (
    input  wire clk,
    input  wire rst,
    input  wire en,
    input  wire d,
    output reg  q,
    output wire qbar
);

    assign qbar = ~q;

    always @(posedge clk or posedge rst) begin
        if (rst)
            q <= 1'b0;
        else if (en)
            q <= d;
    end

endmodule

`default_nettype wire
