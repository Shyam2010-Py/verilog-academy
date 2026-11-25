`default_nettype none
`timescale 1ns / 1ps

module adders_tb;
    reg  ha_a, ha_b;
    wire ha_sum, ha_carry;

    reg  fa_a, fa_b, fa_cin;
    wire fa_sum, fa_carry;

    integer i;
    integer errors;
    integer ha_value;
    integer fa_value;
    reg [1:0] ha_result;

    half_adder ha (
        .a(ha_a), .b(ha_b),
        .sum(ha_sum), .carry(ha_carry)
    );

    full_adder fa (
        .a(fa_a), .b(fa_b), .cin(fa_cin),
        .sum(fa_sum), .carry(fa_carry)
    );

    initial begin
        errors = 0;

        $display("HALF ADDER");
        $display("a b | sum carry | a+b");
        $display("----+-----------+----");
        for (i = 0; i < 4; i = i + 1) begin
            {ha_a, ha_b} = i[1:0];
            #1;
            ha_result = {ha_carry, ha_sum};
            ha_value = ha_a + ha_b;
            if (ha_result !== ha_value) errors = errors + 1;
            $display(" %b %b |  %b    %b    |  %0d", ha_a, ha_b, ha_sum, ha_carry, ha_value);
        end

        $display("");
        $display("FULL ADDER");
        $display("a b cin | sum carry | a+b+cin");
        $display("--------+-----------+--------");
        for (i = 0; i < 8; i = i + 1) begin
            {fa_a, fa_b, fa_cin} = i[2:0];
            #1;
            fa_value = fa_a + fa_b + fa_cin;
            if ({fa_carry, fa_sum} !== fa_value) errors = errors + 1;
            $display(" %b %b  %b  |  %b    %b    |    %0d",
                     fa_a, fa_b, fa_cin, fa_sum, fa_carry, fa_value);
        end

        $display("checked 12 input combinations, mismatches = %0d", errors);
        $finish;
    end
endmodule

`default_nettype wire
