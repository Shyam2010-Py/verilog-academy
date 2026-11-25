`default_nettype none
`timescale 1ns / 1ps

module routing_tb;
    reg  [3:0] d;
    reg  [1:0] sel;
    reg        en;
    reg        din;
    reg  [3:0] req;
    wire       mux_y;
    wire [3:0] dec_y;
    wire [3:0] demux_y;
    wire       valid;
    wire [1:0] code;
    integer i;

    mux4        u_mux   (.d(d), .sel(sel), .y(mux_y));
    dec2to4     u_dec   (.a(sel), .en(en), .y(dec_y));
    demux1to4   u_demux (.d(din), .sel(sel), .y(demux_y));
    priority4   u_prio  (.req(req), .valid(valid), .code(code));

    initial begin
        d = 4'b1010;
        en = 1;
        din = 1;

        $display("mux: d=%b", d);
        $display("sel | mux | decoder | demux");
        $display("----+-----+---------+------");
        for (i = 0; i < 4; i = i + 1) begin
            sel = i[1:0];
            #1;
            $display(" %b  |  %b  |  %b   | %b", sel, mux_y, dec_y, demux_y);
        end

        $display("priority encoder:");
        $display("req  | valid code");
        $display("-----+-----------");
        req = 4'b0000; #1; $display("%b |   %b    %b", req, valid, code);
        req = 4'b0001; #1; $display("%b |   %b    %b", req, valid, code);
        req = 4'b0010; #1; $display("%b |   %b    %b", req, valid, code);
        req = 4'b0100; #1; $display("%b |   %b    %b", req, valid, code);
        req = 4'b1000; #1; $display("%b |   %b    %b", req, valid, code);
        req = 4'b1010; #1; $display("%b |   %b    %b", req, valid, code);

        $finish;
    end
endmodule
`default_nettype wire
