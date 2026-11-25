`default_nettype none
`timescale 1ns / 1ps

module blocking_tb;
    reg       clk;
    reg       d;
    wire      b0;
    wire      b1;
    wire      b2;
    wire      n0;
    wire      n1;
    wire      n2;
    reg [5:0] pattern;
    integer   i;

    shift_blocking    u_block (.clk(clk), .d(d), .q0(b0), .q1(b1), .q2(b2));
    shift_nonblocking u_nonblk (.clk(clk), .d(d), .q0(n0), .q1(n1), .q2(n2));

    always #5 clk = ~clk;

    initial begin
        clk     = 1'b0;
        d       = 1'b0;
        pattern = 6'b110100;

        $display("cycle d | blocking q2q1q0 | nonblocking q2q1q0");
        $display("------+-+----------------+-------------------");

        for (i = 0; i < 6; i = i + 1) begin
            @(negedge clk);
            d = pattern[5 - i];
            @(posedge clk);
            #1;
            $display("  %0d   %b |      %b%b%b       |       %b%b%b",
                     i, d, b2, b1, b0, n2, n1, n0);
        end
        $finish;
    end
endmodule
`default_nettype wire
