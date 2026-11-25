`default_nettype none
`timescale 1ns / 1ps

// EC-410 Experiment 06 - 1:2, 1:4 and 1:8 demultiplexers.
// Exactly one output receives din; every unselected output is forced to 0.

module demux1_2 (
    input  wire din,
    input  wire s,
    output wire y0,
    output wire y1
);

    assign y0 = din & ~s;
    assign y1 = din &  s;

endmodule


module demux1_4 (
    input  wire       din,
    input  wire [1:0] s,
    output reg  [3:0] y
);

    always @* begin
        y = 4'b0000;
        case (s)
            2'b00: y[0] = din;
            2'b01: y[1] = din;
            2'b10: y[2] = din;
            2'b11: y[3] = din;
            default: y = 4'b0000;
        endcase
    end

endmodule


module demux1_8 (
    input  wire       din,
    input  wire [2:0] s,
    output reg  [7:0] y
);

    always @* begin
        y = 8'b00000000;
        case (s)
            3'b000: y[0] = din;
            3'b001: y[1] = din;
            3'b010: y[2] = din;
            3'b011: y[3] = din;
            3'b100: y[4] = din;
            3'b101: y[5] = din;
            3'b110: y[6] = din;
            3'b111: y[7] = din;
            default: y = 8'b00000000;
        endcase
    end

endmodule

`default_nettype wire
