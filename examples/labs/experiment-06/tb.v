`default_nettype none
`timescale 1ns / 1ps

module demultiplexers_tb;
    reg  d2_din, d2_s;
    wire d2_y0, d2_y1;

    reg  d4_din;
    reg  [1:0] d4_s;
    wire [3:0] d4_y;

    reg  d8_din;
    reg  [2:0] d8_s;
    wire [7:0] d8_y;

    integer s, din;
    integer errors;
    integer checks;
    reg [3:0] expected4;
    reg [7:0] expected8;

    demux1_2 u_demux1_2 (.din(d2_din), .s(d2_s), .y0(d2_y0), .y1(d2_y1));
    demux1_4 u_demux1_4 (.din(d4_din), .s(d4_s), .y(d4_y));
    demux1_8 u_demux1_8 (.din(d8_din), .s(d8_s), .y(d8_y));

    initial begin
        errors = 0;
        checks = 0;

        $display("1:2 DEMULTIPLEXER");
        $display("din s | y1 y0 | active (-1=none)");
        $display("------+-------+-------");
        for (din = 0; din < 2; din = din + 1) begin
            for (s = 0; s < 2; s = s + 1) begin
                d2_din = din[0];
                d2_s = s[0];
                #1;
                checks = checks + 1;
                if ({d2_y1, d2_y0} !== (din ? (s ? 2'b10 : 2'b01) : 2'b00)) errors = errors + 1;
                $display(" %b   %b |  %b  %b | %0d", d2_din, d2_s, d2_y1, d2_y0,
                         din ? s : -1);
            end
        end

        $display("");
        $display("1:4 DEMULTIPLEXER");
        $display("din s1 s0 | y3 y2 y1 y0 | active (-1=none)");
        $display("----------+-------------+-------");
        for (din = 0; din < 2; din = din + 1) begin
            for (s = 0; s < 4; s = s + 1) begin
                d4_din = din[0];
                d4_s = s[1:0];
                #1;
                checks = checks + 1;
                expected4 = din ? (4'b0001 << s) : 4'b0000;
                if (d4_y !== expected4) errors = errors + 1;
                $display(" %b   %b  %b |  %b  %b  %b  %b | %0d",
                         d4_din, d4_s[1], d4_s[0],
                         d4_y[3], d4_y[2], d4_y[1], d4_y[0],
                         din ? s : -1);
            end
        end

        $display("");
        $display("1:8 DEMULTIPLEXER");
        $display("din s2 s1 s0 | y7 y6 y5 y4 y3 y2 y1 y0 | active (-1=none)");
        $display("-------------+--------------------------+-------");
        for (din = 0; din < 2; din = din + 1) begin
            for (s = 0; s < 8; s = s + 1) begin
                d8_din = din[0];
                d8_s = s[2:0];
                #1;
                checks = checks + 1;
                expected8 = din ? (8'b00000001 << s) : 8'b00000000;
                if (d8_y !== expected8) errors = errors + 1;
                $display(" %b   %b  %b  %b |  %b  %b  %b  %b  %b  %b  %b  %b | %0d",
                         d8_din, d8_s[2], d8_s[1], d8_s[0],
                         d8_y[7], d8_y[6], d8_y[5], d8_y[4],
                         d8_y[3], d8_y[2], d8_y[1], d8_y[0],
                         din ? s : -1);
            end
        end

        $display("");
        $display("checked %0d data/select combinations, mismatches = %0d", checks, errors);
        $finish;
    end
endmodule

`default_nettype wire

