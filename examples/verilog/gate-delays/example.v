`timescale 1ns / 1ps
`default_nettype none
// Two delay values: rise = 3 ns, fall = 5 ns.
module delay_demo (
    input  wire a,
    input  wire b,
    output wire y,
    output wire yn
);
    and #(3, 5) g_and (y, a, b);
    not #(2)    g_not (yn, a);
endmodule

module delay_tb;
    reg  a;
    reg  b;
    wire y;
    wire yn;

    delay_demo dut (.a(a), .b(b), .y(y), .yn(yn));

    initial begin
        a = 0;
        b = 0;
        $monitor("t=%0t a=%b b=%b y=%b yn=%b", $time, a, b, y, yn);

        #10 a = 1;
        #10 b = 1;
        #10 a = 0;
        #30 $finish;
    end
endmodule
`default_nettype wire
