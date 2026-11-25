`timescale 1ns / 1ps
`define WIDTH 4
`default_nettype none
// Simulation tasks are for observation, not for synthesis.
module system_tasks_tb;
    reg clk;
    reg [`WIDTH-1:0] count;
    reg value;

    initial begin
        clk   = 0;
        count = 0;
        value = 0;

        $display("start at t=%0t", $time);
        #5;
        count = 4'b0011;
        $display("count=%b (%0d) at t=%0t", count, count, $time);

        value <= 1'b1;
        $display("display sees value=%b", value);
        $strobe("strobe sees value=%b", value);

        #5;
        $write("write keeps ");
        $write("the line open\n");
        $display("finish at t=%0t", $time);
        $finish;
    end

    always #2 clk = ~clk;
endmodule
`default_nettype wire
