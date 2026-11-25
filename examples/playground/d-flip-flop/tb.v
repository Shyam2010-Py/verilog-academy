`default_nettype none
`timescale 1ns / 1ps

module d_flip_flop_tb;
    reg  clk;
    reg  rst;
    reg  en;
    reg  d;
    wire q;
    wire qbar;
    integer checks;
    integer errors;

    d_flip_flop dut (.clk(clk), .rst(rst), .en(en), .d(d), .q(q), .qbar(qbar));

    task pulse_clock;
        begin
            clk = 1'b1;
            #5;
            clk = 1'b0;
            #5;
        end
    endtask

    task check_state;
        input expected_q;
        begin
            #1;
            checks = checks + 1;
            if (q !== expected_q || qbar !== ~expected_q) begin
                errors = errors + 1;
                $display("FAIL: expected Q=%b, got Q=%b Qbar=%b", expected_q, q, qbar);
            end
        end
    endtask

    initial begin
        checks = 0;
        errors = 0;
        clk = 1'b0;
        rst = 1'b0;
        en  = 1'b0;
        d   = 1'b0;
        #1;
        rst = 1'b1;
        check_state(1'b0);
        $display("D flip-flop: asynchronous reset, enable and rising edge");
        $display("RST EN D CLK     | Q Qbar");
        $display("-----------------+-------");
        $display(" 1  0 0  async   | %b  %b", q, qbar);

        rst = 1'b0;
        en  = 1'b1;
        d   = 1'b1;
        check_state(1'b0);
        $display(" 0  1 1  no edge | %b  %b", q, qbar);

        pulse_clock;
        check_state(1'b1);
        $display(" 0  1 1  rising  | %b  %b", q, qbar);

        d = 1'b0;
        check_state(1'b1);
        $display(" 0  1 0  no edge | %b  %b", q, qbar);

        pulse_clock;
        check_state(1'b0);
        $display(" 0  1 0  rising  | %b  %b", q, qbar);

        en = 1'b0;
        d  = 1'b1;
        pulse_clock;
        check_state(1'b0);
        $display(" 0  0 1  rising  | %b  %b", q, qbar);

        en = 1'b1;
        pulse_clock;
        check_state(1'b1);
        $display(" 0  1 1  rising  | %b  %b", q, qbar);

        rst = 1'b1;
        check_state(1'b0);
        $display(" 1  1 1  async   | %b  %b", q, qbar);

        if (errors == 0) $display("PASS: %0d/%0d state checks match", checks, checks);
        else $display("FAIL: %0d of %0d checks failed", errors, checks);
        $finish;
    end
endmodule

`default_nettype wire
