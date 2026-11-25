`default_nettype none
`timescale 1ns / 1ps

module gate_demo_tb;
    reg  a;
    reg  b;
    wire y_and;
    wire y_or;
    wire y_xor;
    wire y_nand;
    wire y_nor;
    wire y_not;
    wire y_tri;
    integer i;

    gate_demo dut (
        .a(a), .b(b),
        .y_and(y_and), .y_or(y_or), .y_xor(y_xor),
        .y_nand(y_nand), .y_nor(y_nor), .y_not(y_not),
        .y_tri(y_tri)
    );

    initial begin
        $display("a b | and or xor nand nor not tri(b)");
        $display("----+--------------------------------");
        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #1;
            $display(" %b %b |  %b   %b   %b    %b    %b   %b    %b",
                     a, b, y_and, y_or, y_xor, y_nand, y_nor, y_not, y_tri);
        end
        $finish;
    end
endmodule
`default_nettype wire
