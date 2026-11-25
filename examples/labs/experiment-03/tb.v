`default_nettype none
`timescale 1ns / 1ps

module subtractors_tb;
    reg  hs_x, hs_y;
    wire hs_diff, hs_borrow;

    reg  fs_x, fs_y, fs_bin;
    wire fs_diff, fs_borrow;

    integer i;
    integer errors;
    integer expected_value;
    integer expected_borrow;

    half_subtractor hs (
        .x(hs_x), .y(hs_y),
        .diff(hs_diff), .borrow(hs_borrow)
    );

    full_subtractor fs (
        .x(fs_x), .y(fs_y), .bin(fs_bin),
        .diff(fs_diff), .borrow(fs_borrow)
    );

    initial begin
        errors = 0;

        $display("HALF SUBTRACTOR");
        $display("x y | diff borrow | x-y");
        $display("----+-------------+----");
        for (i = 0; i < 4; i = i + 1) begin
            {hs_x, hs_y} = i[1:0];
            #1;
            expected_value = hs_x;
            expected_value = expected_value - hs_y;
            expected_borrow = (expected_value < 0);
            if ({hs_borrow, hs_diff} !== {expected_borrow[0], expected_value[0]}) begin
                errors = errors + 1;
            end
            $display(" %b %b |  %b     %b    | %0d", hs_x, hs_y, hs_diff, hs_borrow, expected_value);
        end

        $display("");
        $display("FULL SUBTRACTOR");
        $display("x y bin | diff borrow | result");
        $display("--------+-------------+-------");
        for (i = 0; i < 8; i = i + 1) begin
            {fs_x, fs_y, fs_bin} = i[2:0];
            #1;
            expected_value = fs_x;
            expected_value = expected_value - fs_y;
            expected_value = expected_value - fs_bin;
            expected_borrow = (expected_value < 0);
            if ({fs_borrow, fs_diff} !== {expected_borrow[0], expected_value[0]}) begin
                errors = errors + 1;
            end
            $display(" %b %b  %b  |  %b     %b    |  %0d",
                     fs_x, fs_y, fs_bin, fs_diff, fs_borrow, expected_value);
        end

        $display("checked 12 input combinations, mismatches = %0d", errors);
        $finish;
    end
endmodule

`default_nettype wire
