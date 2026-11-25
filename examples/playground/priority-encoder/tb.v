`default_nettype none
`timescale 1ns / 1ps

module priority_encoder_4_to_2_tb;
    reg  [3:0] req;
    wire [1:0] code;
    wire       valid;
    reg  [1:0] exp_code;
    reg        exp_valid;
    integer ri;
    integer checks;
    integer errors;

    priority_encoder_4_to_2 dut (.req(req), .code(code), .valid(valid));

    initial begin
        checks = 0;
        errors = 0;
        $display("4-to-2 priority encoder");
        $display("req  | code valid");
        $display("-----+-----------");
        for (ri = 0; ri < 16; ri = ri + 1) begin
            req = ri;
            #1;
            casez (req)
                4'b1???: exp_code = 2'd3;
                4'b01??: exp_code = 2'd2;
                4'b001?: exp_code = 2'd1;
                4'b0001: exp_code = 2'd0;
                default: exp_code = 2'd0;
            endcase
            exp_valid = |req;
            checks = checks + 1;
            if (code !== exp_code) errors = errors + 1;
            if (valid !== exp_valid) errors = errors + 1;
            $display("%b |  %b    %b", req, code, valid);
        end
        $display("Checked %0d request patterns", checks);
        if (errors == 0) $display("PASS: 16/16 patterns match");
        else $display("FAIL: %0d mismatches", errors);
        $finish;
    end
endmodule

`default_nettype wire
