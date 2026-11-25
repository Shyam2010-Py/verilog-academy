`default_nettype none
`timescale 1ns / 1ps

// A 4:1 multiplexer selects one of four data bits with a two-bit select.
module mux_4_to_1 (
    input  wire [3:0] d,
    input  wire [1:0] sel,
    output reg        y
);

    always @* begin
        case (sel)
            2'b00: y = d[0];
            2'b01: y = d[1];
            2'b10: y = d[2];
            2'b11: y = d[3];
            default: y = 1'b0;
        endcase
    end

endmodule

`default_nettype wire
