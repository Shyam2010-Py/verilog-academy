`default_nettype none
`timescale 1ns / 1ps

module timing_tb;
    reg       clk;
    reg       start;
    reg [1:0] state;

    always #5 clk = ~clk;

    // The counter advances only while start is high.
    always @(posedge clk) begin
        if (start && state < 2'd3)
            state <= state + 2'd1;
    end

    initial begin
        clk   = 1'b0;
        start = 1'b0;
        state = 2'd0;

        #7 start = 1'b1;
        $display("t=%0t delay: start raised", $time);

        @(posedge clk);
        $display("t=%0t event: first posedge after start", $time);

        wait (state == 2'd2);
        $display("t=%0t wait: state reached %0d", $time, state);

        #3 $display("t=%0t delay: three time units later", $time);
        $finish;
    end
endmodule
`default_nettype wire
