`default_nettype none
`timescale 1ns / 1ps

module basic_gates_tb;
    reg  a;
    reg  b;
    wire y_and, y_or, y_not, y_nand, y_nor, y_xor, y_xnor;

    reg [6:0] expected;
    reg [6:0] actual;
    integer i;
    integer errors;

    basic_gates dut (
        .a(a), .b(b),
        .y_and(y_and), .y_or(y_or), .y_not(y_not),
        .y_nand(y_nand), .y_nor(y_nor),
        .y_xor(y_xor), .y_xnor(y_xnor)
    );

    initial begin
        errors = 0;
        $display("a b | and or not nand nor xor xnor | result");
        $display("----+--------------------------------+-------");

        for (i = 0; i < 4; i = i + 1) begin
            {a, b} = i[1:0];
            #1;
            actual = {y_and, y_or, y_not, y_nand, y_nor, y_xor, y_xnor};

            case ({a, b})
                2'b00: expected = 7'b0011101;
                2'b01: expected = 7'b0111010;
                2'b10: expected = 7'b0101010;
                2'b11: expected = 7'b1100001;
                default: expected = 7'bxxxxxxx;
            endcase

            if (actual !== expected) begin
                errors = errors + 1;
                $display(" %b %b |  %b   %b   %b    %b    %b   %b    %b | FAIL",
                         a, b, y_and, y_or, y_not, y_nand, y_nor, y_xor, y_xnor);
            end else begin
                $display(" %b %b |  %b   %b   %b    %b    %b   %b    %b | pass",
                         a, b, y_and, y_or, y_not, y_nand, y_nor, y_xor, y_xnor);
            end
        end

        $display("checked 4 input combinations, mismatches = %0d", errors);
        $finish;
    end
endmodule

`default_nettype wire
