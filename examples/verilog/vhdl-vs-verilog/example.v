`default_nettype none
// The same two-input AND function shown in the VHDL comparison.
module and2 (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a & b;
endmodule

module and2_tb;
    reg  a;
    reg  b;
    wire y;
    integer i;

    and2 dut (.a(a), .b(b), .y(y));

    initial begin
        $display("a b | y");
        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #1;
            $display("%b %b | %b", a, b, y);
        end
        $finish;
    end
endmodule
`default_nettype wire
