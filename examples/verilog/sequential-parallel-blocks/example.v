`default_nettype none
`timescale 1ns / 1ps

module blocks_tb;
    reg a;
    reg b;
    reg c;

    // Sequential: each statement waits for the previous one.
    initial begin : sequential_demo
        $display("t=%0t sequential: block starts", $time);
        #2 a = 1'b1;
        $display("t=%0t sequential: a set", $time);
        #2 b = 1'b1;
        $display("t=%0t sequential: b set", $time);
        #2 c = 1'b1;
        $display("t=%0t sequential: c set, block ends", $time);
    end

    // Parallel: every branch starts at the same time.
    initial begin : parallel_demo
        #12;
        $display("t=%0t parallel: fork starts", $time);
        fork
            begin
                #4 a = 1'b0;
                $display("t=%0t parallel: a cleared", $time);
            end
            begin
                #6 b = 1'b0;
                $display("t=%0t parallel: b cleared", $time);
            end
            begin
                #8 c = 1'b0;
                $display("t=%0t parallel: c cleared", $time);
            end
        join
        $display("t=%0t parallel: join complete a=%b b=%b c=%b",
                 $time, a, b, c);
        $finish;
    end
endmodule
`default_nettype wire
