`default_nettype none
`timescale 1ns / 1ps

module multiplexers_tb;
    reg  m2_d0, m2_d1, m2_s;
    wire m2_y;

    reg  [3:0] m4_d;
    reg  [1:0] m4_s;
    wire m4_y;

    reg  [7:0] m8_d;
    reg  [2:0] m8_s;
    wire m8_y;

    integer s, pattern;
    integer errors;
    integer checks;

    mux2 u_mux2 (.d0(m2_d0), .d1(m2_d1), .s(m2_s), .y(m2_y));
    mux4 u_mux4 (.d(m4_d), .s(m4_s), .y(m4_y));
    mux8 u_mux8 (.d(m8_d), .s(m8_s), .y(m8_y));

    initial begin
        errors = 0;
        checks = 0;

        $display("2:1 MULTIPLEXER - every data pattern and both selects");
        $display("s d1 d0 | y | selected");
        $display("--------+---+---------");
        for (s = 0; s < 2; s = s + 1) begin
            for (pattern = 0; pattern < 4; pattern = pattern + 1) begin
                {m2_d1, m2_d0} = pattern[1:0];
                m2_s = s[0];
                #1;
                checks = checks + 1;
                if (m2_y !== (s ? m2_d1 : m2_d0)) errors = errors + 1;
                $display(" %b  %b  %b | %b | %s", m2_s, m2_d1, m2_d0, m2_y,
                         s ? "d1" : "d0");
            end
        end

        $display("");
        $display("4:1 MULTIPLEXER - path check with d = 1010");
        $display("s1 s0 | y | selected");
        $display("-------+---+---------");
        m4_d = 4'b1010;
        for (s = 0; s < 4; s = s + 1) begin
            m4_s = s[1:0];
            #1;
            checks = checks + 1;
            if (m4_y !== m4_d[s]) errors = errors + 1;
            $display(" %b  %b  | %b | d%0d", m4_s[1], m4_s[0], m4_y, s);
        end
        for (s = 0; s < 4; s = s + 1) begin
            for (pattern = 0; pattern < 16; pattern = pattern + 1) begin
                m4_d = pattern[3:0];
                m4_s = s[1:0];
                #1;
                checks = checks + 1;
                if (m4_y !== m4_d[s]) errors = errors + 1;
            end
        end
        $display("exhaustive data patterns for all 4 selects: 64 checks");

        $display("");
        $display("8:1 MULTIPLEXER - path check with d = 10101010");
        $display("s2 s1 s0 | y | selected");
        $display("---------+---+---------");
        m8_d = 8'b10101010;
        for (s = 0; s < 8; s = s + 1) begin
            m8_s = s[2:0];
            #1;
            checks = checks + 1;
            if (m8_y !== m8_d[s]) errors = errors + 1;
            $display(" %b  %b  %b  | %b | d%0d", m8_s[2], m8_s[1], m8_s[0], m8_y, s);
        end
        for (s = 0; s < 8; s = s + 1) begin
            for (pattern = 0; pattern < 256; pattern = pattern + 1) begin
                m8_d = pattern[7:0];
                m8_s = s[2:0];
                #1;
                checks = checks + 1;
                if (m8_y !== m8_d[s]) errors = errors + 1;
            end
        end
        $display("exhaustive data patterns for all 8 selects: 2048 checks");

        $display("");
        $display("checked %0d data/select combinations, mismatches = %0d", checks, errors);
        $finish;
    end
endmodule

`default_nettype wire
