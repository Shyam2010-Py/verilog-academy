`default_nettype none
`timescale 1ns / 1ps

module four_bit_adder_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg        cin;
    wire [3:0] sum;
    wire       cout;
    wire       overflow;
    reg  [4:0] expected_sum;
    integer ai;
    integer bi;
    integer ci;
    integer checks;
    integer errors;

    four_bit_adder dut (
        .a(a), .b(b), .cin(cin),
        .sum(sum), .cout(cout), .overflow(overflow)
    );

    initial begin
        checks = 0;
        errors = 0;
        $display("4-bit ripple-carry adder");
        $display("A    B    Cin | Cout Sum  OVF");
        $display("---------------+--------------");
        for (ai = 0; ai < 16; ai = ai + 1) begin
            for (bi = 0; bi < 16; bi = bi + 1) begin
                for (ci = 0; ci < 2; ci = ci + 1) begin
                    a = ai;
                    b = bi;
                    cin = ci[0];
                    #1;
                    expected_sum = {1'b0, a} + {1'b0, b} + cin;
                    checks = checks + 1;
                    if ({cout, sum} !== expected_sum) errors = errors + 1;
                    if (overflow !== ((a[3] & b[3] & ~sum[3]) | (~a[3] & ~b[3] & sum[3]))) errors = errors + 1;
                    if (((a == 4'd0)  && (b == 4'd0)  && (cin == 1'b0)) ||
                        ((a == 4'd10) && (b == 4'd5)  && (cin == 1'b0)) ||
                        ((a == 4'd15) && (b == 4'd1)  && (cin == 1'b0)) ||
                        ((a == 4'd8)  && (b == 4'd8)  && (cin == 1'b0)) ||
                        ((a == 4'd15) && (b == 4'd15) && (cin == 1'b1)))
                        $display("%b %b   %b  |  %b   %b   %b", a, b, cin, cout, sum, overflow);
                end
            end
        end
        $display("Checked %0d input combinations", checks);
        if (errors == 0) $display("PASS: 512/512 combinations match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
