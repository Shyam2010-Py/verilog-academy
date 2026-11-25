`default_nettype none
`timescale 1ns / 1ps

module alu_compare_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg  [1:0] op;
    wire [3:0] y_flow;
    wire [3:0] y_beh;
    integer ai;
    integer bi;
    integer oi;
    integer checks;
    integer mismatches;

    alu4_dataflow    u_flow (.a(a), .b(b), .op(op), .y(y_flow));
    alu4_behavioural u_beh  (.a(a), .b(b), .op(op), .y(y_beh));

    initial begin
        checks     = 0;
        mismatches = 0;

        // Exhaustive equivalence check over every input combination.
        for (ai = 0; ai < 16; ai = ai + 1) begin
            for (bi = 0; bi < 16; bi = bi + 1) begin
                for (oi = 0; oi < 4; oi = oi + 1) begin
                    a  = ai[3:0];
                    b  = bi[3:0];
                    op = oi[1:0];
                    #1;
                    checks = checks + 1;
                    if (y_flow !== y_beh) begin
                        mismatches = mismatches + 1;
                        $display("MISMATCH a=%b b=%b op=%b dataflow=%b behavioural=%b",
                                 a, b, op, y_flow, y_beh);
                    end
                end
            end
        end
        $display("compared %0d input combinations, mismatches = %0d", checks, mismatches);

        a = 4'b1010;
        b = 4'b0101;
        $display("a=%b (10)  b=%b (5)", a, b);
        $display("op | result | decimal");
        $display("---+--------+--------");
        for (oi = 0; oi < 4; oi = oi + 1) begin
            op = oi[1:0];
            #1;
            $display("%b |  %b  |    %2d", op, y_flow, y_flow);
        end
        $finish;
    end
endmodule
`default_nettype wire
