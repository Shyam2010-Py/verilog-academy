`default_nettype none
`timescale 1ns / 1ps

// EC-410 Experiment 05 - 2:1, 4:1 and 8:1 multiplexers.
// The 2:1 mux uses a conditional assignment; the wider muxes use a case
// statement so the selected input is explicit for every select value.

module mux2 (
    input  wire d0,
    input  wire d1,
    input  wire s,
    output wire y
);

    assign y = s ? d1 : d0;

endmodule


module mux4 (
    input  wire [3:0] d,
    input  wire [1:0] s,
    output reg        y
);

    always @* begin
        case (s)
            2'b00: y = d[0];
            2'b01: y = d[1];
            2'b10: y = d[2];
            2'b11: y = d[3];
            default: y = 1'b0;
        endcase
    end

endmodule


module mux8 (
    input  wire [7:0] d,
    input  wire [2:0] s,
    output reg        y
);

    always @* begin
        case (s)
            3'b000: y = d[0];
            3'b001: y = d[1];
            3'b010: y = d[2];
            3'b011: y = d[3];
            3'b100: y = d[4];
            3'b101: y = d[5];
            3'b110: y = d[6];
            3'b111: y = d[7];
            default: y = 1'b0;
        endcase
    end

endmodule

`default_nettype wire
