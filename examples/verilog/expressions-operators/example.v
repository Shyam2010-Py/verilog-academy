`default_nettype none
// Width, signedness and operator behaviour.
module expressions_tb;
    reg [3:0] a;
    reg [3:0] b;
    reg signed [3:0] s;

    initial begin
        a = 4'b1010;
        b = 4'b0101;
        s = -3;

        $display("a=%b b=%b s=%0d", a, b, s);
        $display("a & b   = %b", a & b);
        $display("a | b   = %b", a | b);
        $display("a ^ b   = %b", a ^ b);
        $display("~a      = %b", ~a);
        $display("&a |a ^a = %b %b %b", &a, |a, ^a);
        $display("a && b  = %b (logical)", a && b);
        $display("a == b  = %b", a == b);
        $display("1'b1 == 1'bx  = %b", 1'b1 == 1'bx);
        $display("1'b1 === 1'bx = %b", 1'b1 === 1'bx);
        $display("15 + 1 at 4 bits = %b (%0d)", 4'd15 + 4'd1, 4'd15 + 4'd1);
        $display("s >>> 1 = %b (%0d)", s >>> 1, s >>> 1);
        $display("a >> 1  = %b", a >> 1);
        $display("a[0] ? b : a = %b", a[0] ? b : a);
        $display("-1 < 0    = %b", -1 < 0);
        $display("4'b1111 > 0 = %b", 4'b1111 > 0);
        $finish;
    end
endmodule
`default_nettype wire
