`default_nettype none
`timescale 1ns / 1ps

module demux_1_to_4_tb;
    reg        din;
    reg  [1:0] sel;
    wire [3:0] y;
    reg  [3:0] expected;
    integer di;
    integer si;
    integer checks;
    integer errors;

    demux_1_to_4 dut (.din(din), .sel(sel), .y(y));

    initial begin
        checks = 0;
        errors = 0;
        $display("1:4 demultiplexer");
        $display("din sel | y3 y2 y1 y0");
        $display("----+-----+-----------");
        for (di = 0; di < 2; di = di + 1) begin
            din = di[0];
            for (si = 0; si < 4; si = si + 1) begin
                sel = si;
                #1;
                expected = 4'b0000;
                case (sel)
                    2'd0: expected[0] = din;
                    2'd1: expected[1] = din;
                    2'd2: expected[2] = din;
                    default: expected[3] = din;
                endcase
                checks = checks + 1;
                if (y !== expected) errors = errors + 1;
                $display(" %b   %b |  %b", din, sel, y);
            end
        end
        $display("Checked %0d data/select combinations", checks);
        if (errors == 0) $display("PASS: 8/8 combinations match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
