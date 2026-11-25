`default_nettype none
`timescale 1ns / 1ps

module udp_tb;
    reg  sel;
    reg  a;
    reg  b;
    reg  en;
    reg  d;
    wire mux_out;
    wire q;
    integer i;

    mux2_udp   u_mux (.out(mux_out), .sel(sel), .a(a), .b(b));
    dlatch_udp u_lat (.q(q), .en(en), .d(d));

    initial begin
        $display("combinational UDP: 2:1 mux");
        $display("sel a b | out");
        $display("--------+----");
        for (i = 0; i < 8; i = i + 1) begin
            {sel, a, b} = i[2:0];
            #1;
            $display(" %b  %b %b |  %b", sel, a, b, mux_out);
        end

        $display("sequential UDP: transparent D latch");
        en = 1'b1;
        d  = 1'b1;
        #1;
        $display("en=%b d=%b -> q=%b", en, d, q);

        en = 1'b0;
        d  = 1'b0;
        #1;
        $display("en=%b d=%b -> q=%b (held)", en, d, q);

        en = 1'b1;
        d  = 1'b0;
        #1;
        $display("en=%b d=%b -> q=%b", en, d, q);

        $finish;
    end
endmodule
`default_nettype wire
