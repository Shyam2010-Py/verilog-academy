`default_nettype none
`timescale 1ns / 1ps

module half_adder_tb;
    reg  a;
    reg  b;
    wire sum;
    wire carry;
    integer i;

    half_adder dut (.a(a), .b(b), .sum(sum), .carry(carry));

    initial begin
        $display("a b | sum carry");
        $display("----+----------");
        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #1;
            $display(" %b %b |  %b    %b", a, b, sum, carry);
        end
        $finish;
    end
endmodule
`default_nettype wire
