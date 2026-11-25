`default_nettype none
`timescale 1ns / 1ps

module logic_pair_tb;
    reg  a;
    reg  b;
    wire y_and;
    wire y_or;
    integer i;

    logic_pair dut (
        .a(a),
        .b(b),
        .y_and(y_and),
        .y_or(y_or)
    );

    initial begin
        $display("a b | and or");
        $display("----+--------");
        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #1;
            $display(" %b %b |  %b   %b", a, b, y_and, y_or);
        end
        $finish;
    end
endmodule
`default_nettype wire
