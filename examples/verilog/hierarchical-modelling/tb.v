`default_nettype none
`timescale 1ns / 1ps

module rca4_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg        cin;
    wire [3:0] sum;
    wire       cout;
    integer i;

    rca4 dut (.a(a), .b(b), .cin(cin), .sum(sum), .cout(cout));

    initial begin
        $display(" a   b  cin | sum cout | decimal");
        $display("------------+----------+--------");
        for (i = 0; i < 16; i = i + 1) begin
            a   = i[3:0];
            b   = 4'd5;
            cin = i[0];
            #1;
            $display("%2d  %2d    %b | %4b   %b   |  %2d", a, b, cin, sum, cout, {cout, sum});
        end
        $finish;
    end
endmodule
`default_nettype wire
