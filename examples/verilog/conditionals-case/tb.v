`default_nettype none
`timescale 1ns / 1ps

module case_tb;
    reg  [3:0] req;
    wire [1:0] code_if;
    wire [1:0] code_cz;
    wire       valid_if;
    wire       valid_cz;
    reg        en;
    reg        d_latch;
    wire       q_latch;
    integer    i;
    integer    mismatches;

    prio_if    u_if  (.req(req), .code(code_if), .valid(valid_if));
    prio_casez u_cz  (.req(req), .code(code_cz), .valid(valid_cz));
    latch_risk u_lat (.en(en), .d(d_latch), .q(q_latch));

    initial begin
        mismatches = 0;
        $display("req  | if: code valid | casez: code valid");
        $display("-----+----------------+-------------------");
        for (i = 0; i < 16; i = i + 1) begin
            req = i[3:0];
            #1;
            if (code_if !== code_cz || valid_if !== valid_cz)
                mismatches = mismatches + 1;
            $display("%b |      %0d     %b   |        %0d     %b",
                     req, code_if, valid_if, code_cz, valid_cz);
        end
        $display("mismatches between if/else and casez: %0d", mismatches);

        en      = 1'b1;
        d_latch = 1'b1;
        #1;
        $display("latch: en=%b d=%b -> q=%b", en, d_latch, q_latch);

        en      = 1'b0;
        d_latch = 1'b0;
        #1;
        $display("latch: en=%b d=%b -> q=%b (held)", en, d_latch, q_latch);

        en      = 1'b1;
        d_latch = 1'b0;
        #1;
        $display("latch: en=%b d=%b -> q=%b", en, d_latch, q_latch);

        $finish;
    end
endmodule
`default_nettype wire
