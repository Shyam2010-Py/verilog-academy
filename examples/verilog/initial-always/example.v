`default_nettype none
`timescale 1ns / 1ps

module initial_always_tb;
    reg       clk;
    reg       reset;
    reg [2:0] count;

    // One clock generator for the whole simulation.
    always #5 clk = ~clk;

    // Synchronous counter: runs on every rising edge.
    always @(posedge clk) begin
        if (reset)
            count <= 3'd0;
        else
            count <= count + 3'd1;
    end

    // One-shot stimulus and observation.
    initial begin
        clk   = 1'b0;
        reset = 1'b1;
        count = 3'd0;
        $display("t=%0t initial: clk=%b reset=%b count=%0d", $time, clk, reset, count);

        #12 reset = 1'b0;
        $display("t=%0t initial: reset released", $time);

        #14 $display("t=%0t sample: count=%0d", $time, count);
        #10 $display("t=%0t sample: count=%0d", $time, count);
        #10 $display("t=%0t sample: count=%0d", $time, count);

        $finish;
    end
endmodule
`default_nettype wire
