`default_nettype none
`timescale 1ns / 1ps

module addsub4_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg        sub;
    wire [3:0] sum;
    wire       cout;
    wire       zero;
    wire       overflow;
    wire       lt;
    wire       eq;
    wire       gt;
    wire       slt;
    wire       seq;
    wire       sgt;

    addsub4 dut (
        .a(a), .b(b), .sub(sub),
        .sum(sum), .cout(cout), .zero(zero), .overflow(overflow)
    );

    comparator4 cmp (.a(a), .b(b), .lt(lt), .eq(eq), .gt(gt));
    comparator4_signed scmp (.a(a), .b(b), .lt(slt), .eq(seq), .gt(sgt));

    initial begin
        $display("operation        | sum  cout zero ovf | lt eq gt");
        $display("-----------------+-------------------+---------");

        a = 4'd5; b = 4'd3; sub = 0; #1;
        $display("5 + 3            | %b   %b    %b    %b  |  %b  %b  %b", sum, cout, zero, overflow, lt, eq, gt);

        a = 4'd7; b = 4'd1; sub = 0; #1;
        $display("7 + 1 (overflow) | %b   %b    %b    %b  |  %b  %b  %b", sum, cout, zero, overflow, lt, eq, gt);

        a = 4'd4; b = 4'd2; sub = 1; #1;
        $display("4 - 2            | %b   %b    %b    %b  |  %b  %b  %b", sum, cout, zero, overflow, lt, eq, gt);

        a = 4'd0; b = 4'd1; sub = 1; #1;
        $display("0 - 1            | %b   %b    %b    %b  |  %b  %b  %b", sum, cout, zero, overflow, lt, eq, gt);

        a = 4'b1000; b = 4'd1; sub = 1; #1;
        $display("-8 - 1 (overflow)| %b   %b    %b    %b  |  %b  %b  %b", sum, cout, zero, overflow, lt, eq, gt);

        a = 4'b1000; b = 4'd1; sub = 0; #1;
        $display("signed compare a=%b (-8) b=%b (1) -> lt=%b eq=%b gt=%b",
                 a, b, slt, seq, sgt);

        $finish;
    end
endmodule
`default_nettype wire
