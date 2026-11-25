`default_nettype none
`timescale 1ns / 1ps

module alu_4_bit_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg  [1:0] op;
    wire [3:0] y;
    reg  [3:0] expected;
    integer checks;
    integer errors;

    alu_4_bit dut (.a(a), .b(b), .op(op), .y(y));

    task check_alu;
        input [1:0] op_value;
        input [3:0] av;
        input [3:0] bv;
        begin
            op = op_value;
            a  = av;
            b  = bv;
            #1;
            case (op)
                2'b00: expected = a & b;
                2'b01: expected = a | b;
                2'b10: expected = a + b;
                default: expected = a - b;
            endcase
            checks = checks + 1;
            if (y !== expected) errors = errors + 1;
            $display("%b | %b %b | %b", op, a, b, y);
        end
    endtask

    initial begin
        checks = 0;
        errors = 0;
        $display("4-bit behavioural ALU");
        $display("op |  a  b  | y");
        $display("---+--------+--");
        check_alu(2'b00, 4'b1010, 4'b0101);
        check_alu(2'b01, 4'b1010, 4'b0101);
        check_alu(2'b10, 4'b1010, 4'b0101);
        check_alu(2'b11, 4'b1010, 4'b0101);
        check_alu(2'b00, 4'b1111, 4'b0001);
        check_alu(2'b01, 4'b1111, 4'b0001);
        check_alu(2'b10, 4'b1111, 4'b0001);
        check_alu(2'b11, 4'b1111, 4'b0001);
        $display("Checked %0d operation/data pairs", checks);
        if (errors == 0) $display("PASS: 8/8 cases match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
