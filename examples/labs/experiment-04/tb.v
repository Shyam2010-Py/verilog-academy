`default_nettype none
`timescale 1ns / 1ps

module parallel_adder_4_tb;
    reg  [3:0] a;
    reg  [3:0] b;
    reg        cin;
    wire [3:0] sum;
    wire       cout;
    wire       overflow;

    integer ai, bi, ci;
    integer errors;
    integer checks;
    integer exact_signed;
    reg [4:0] expected_sum;
    reg expected_overflow;

    parallel_adder_4 dut (
        .a(a), .b(b), .cin(cin),
        .sum(sum), .cout(cout), .overflow(overflow)
    );

    task show_case;
        input [3:0] ta;
        input [3:0] tb;
        input       tc;
        begin
            a = ta; b = tb; cin = tc;
            #1;
            exact_signed = $signed({ta[3], ta}) + $signed({tb[3], tb}) + $signed({1'b0, tc});
            expected_sum = ta + tb + tc;
            expected_overflow = (exact_signed < -8) || (exact_signed > 7);
            $display(" %b + %b + %b = %b  cout=%b overflow=%b",
                     ta, tb, tc, {cout, sum}, cout, overflow);
        end
    endtask

    initial begin
        errors = 0;
        checks = 0;

        $display("SELECTED CASES");
        $display("a     b    cin | sum  cout ovf");
        $display("----------------+--------------");
        show_case(4'b0000, 4'b0000, 1'b0);
        show_case(4'b0011, 4'b0100, 1'b0);
        show_case(4'b0100, 4'b0100, 1'b0);
        show_case(4'b0111, 4'b0001, 1'b0);
        show_case(4'b1000, 4'b0111, 1'b0);
        show_case(4'b1111, 4'b0001, 1'b0);
        show_case(4'b1001, 4'b0111, 1'b0);
        show_case(4'b1000, 4'b1000, 1'b0);
        show_case(4'b1010, 4'b0101, 1'b1);

        $display("");
        $display("EXHAUSTIVE CHECK");
        for (ai = 0; ai < 16; ai = ai + 1) begin
            for (bi = 0; bi < 16; bi = bi + 1) begin
                for (ci = 0; ci < 2; ci = ci + 1) begin
                    a = ai[3:0];
                    b = bi[3:0];
                    cin = ci[0];
                    #1;
                    exact_signed = $signed({a[3], a}) + $signed({b[3], b}) + $signed({1'b0, cin});
                    expected_sum = a + b + cin;
                    expected_overflow = (exact_signed < -8) || (exact_signed > 7);
                    checks = checks + 1;

                    if ({cout, sum} !== expected_sum || overflow !== expected_overflow) begin
                        errors = errors + 1;
                        if (errors <= 3) begin
                            $display("MISMATCH a=%b b=%b cin=%b got=%b ovf=%b expected=%b ovf=%b",
                                     a, b, cin, {cout, sum}, overflow, expected_sum, expected_overflow);
                        end
                    end
                end
            end
        end

        $display("checked %0d combinations, mismatches = %0d", checks, errors);
        $finish;
    end
endmodule

`default_nettype wire
