`default_nettype none
`timescale 1ns / 1ps

module mux_4_to_1_tb;
    reg  [3:0] d;
    reg  [1:0] sel;
    wire       y;
    reg        expected;
    integer si;
    integer di;
    integer checks;
    integer errors;

    mux_4_to_1 dut (.d(d), .sel(sel), .y(y));

    initial begin
        checks = 0;
        errors = 0;
        $display("4:1 multiplexer");
        $display("sel | d3 d2 d1 d0 | y");
        $display("----+-------------+--");
        for (si = 0; si < 4; si = si + 1) begin
            sel = si;
            for (di = 0; di < 16; di = di + 1) begin
                d = di;
                #1;
                case (sel)
                    2'd0: expected = d[0];
                    2'd1: expected = d[1];
                    2'd2: expected = d[2];
                    default: expected = d[3];
                endcase
                checks = checks + 1;
                if (y !== expected) errors = errors + 1;
                if (d == 4'b1010) $display("%b  |  %b | %b", sel, d, y);
            end
        end
        $display("Checked %0d select/data combinations", checks);
        if (errors == 0) $display("PASS: 64/64 combinations match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
