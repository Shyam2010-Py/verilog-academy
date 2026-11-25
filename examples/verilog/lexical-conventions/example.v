`timescale 1ns / 1ps
`default_nettype none
// Number literals, truncation, signedness and replication.
module lexical_tb;
    reg [7:0] byte_a;
    reg [3:0] value;
    reg [3:0] VALUE;
    reg       legal_name_1;

    initial begin
        byte_a = 8'b1010_1010;
        $display("binary 8'b1010_1010  : %b (%h)", byte_a, byte_a);
        $display("hex    8'hA5         : %b (%0d)", 8'hA5, 8'hA5);
        $display("decimal 8'd165       : %h", 8'd165);
        $display("4'd18 truncated      : %b (%0d)", 4'd18, 4'd18);
        $display("signed 8'shFB        : %0d", 8'shFB);
        $display("unsized -5           : %0d", -5);
        $display("replication {4{2'b10}}: %b", {4{2'b10}});
        $display("concatenation {a,b}  : %b", {4'b1100, 4'b1010});

        legal_name_1 = 1'b1;
        value = 4'hA;
        VALUE = 4'h5;
        $display("legal_name_1=%b value=%h VALUE=%h", legal_name_1, value, VALUE);
        $display("value and VALUE are different identifiers");
        $finish;
    end
endmodule
`default_nettype wire
