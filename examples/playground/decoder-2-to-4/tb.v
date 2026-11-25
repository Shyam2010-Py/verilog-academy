`default_nettype none
`timescale 1ns / 1ps

module decoder_2_to_4_tb;
    reg        enable;
    reg  [1:0] addr;
    wire [3:0] y;
    reg  [3:0] expected;
    integer ei;
    integer ai;
    integer checks;
    integer errors;

    decoder_2_to_4 dut (.enable(enable), .addr(addr), .y(y));

    initial begin
        checks = 0;
        errors = 0;
        $display("2-to-4 decoder with enable");
        $display("EN addr | y3 y2 y1 y0");
        $display("--------+-----------");
        for (ei = 0; ei < 2; ei = ei + 1) begin
            enable = ei[0];
            for (ai = 0; ai < 4; ai = ai + 1) begin
                addr = ai;
                #1;
                expected = 4'b0000;
                if (enable) begin
                    case (addr)
                        2'd0: expected = 4'b0001;
                        2'd1: expected = 4'b0010;
                        2'd2: expected = 4'b0100;
                        default: expected = 4'b1000;
                    endcase
                end
                checks = checks + 1;
                if (y !== expected) errors = errors + 1;
                $display(" %b   %b  |  %b", enable, addr, y);
            end
        end
        $display("Checked %0d enable/address combinations", checks);
        if (errors == 0) $display("PASS: 8/8 combinations match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
