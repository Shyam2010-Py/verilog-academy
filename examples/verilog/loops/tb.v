`default_nettype none
`timescale 1ns / 1ps

module loops_tb;
    reg  [3:0] d;
    reg  [7:0] byte_in;
    wire [2:0] ones;
    wire [7:0] reversed;
    integer    i;
    integer    total;

    popcount4 u_pop (.d(d), .count(ones));
    reverse8  u_rev (.d(byte_in), .q(reversed));

    initial begin
        $display("d    | ones");
        $display("-----+-----");
        for (i = 0; i < 16; i = i + 1) begin
            d = i[3:0];
            #1;
            $display("%b |  %0d", d, ones);
        end

        byte_in = 8'b1011_0001;
        #1;
        $display("reverse8(%b) = %b", byte_in, reversed);

        // A while loop and a repeat loop: simulation conveniences.
        total = 0;
        i     = 0;
        while (i < 4) begin
            total = total + i;
            i     = i + 1;
        end
        $display("while loop total 0+1+2+3 = %0d", total);

        repeat (3) $display("repeat block tick");
        $finish;
    end
endmodule
`default_nettype wire
