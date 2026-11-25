`default_nettype none
// WIDTH can be overridden; HALF cannot.
module width_demo #(parameter WIDTH = 4) (
    output wire [7:0] pattern
);
    localparam HALF = WIDTH / 2;

    assign pattern = {HALF{2'b10}};
endmodule

module parameters_tb;
    wire [7:0] p_default;
    wire [7:0] p_override;
    wire [7:0] p_defparam;

    width_demo u_default  (.pattern(p_default));
    width_demo #(.WIDTH(6)) u_override (.pattern(p_override));
    width_demo u_defparam (.pattern(p_defparam));

    // Legacy hierarchical override. Prefer #(...) in new code.
    defparam u_defparam.WIDTH = 8;

    initial begin
        #1;
        $display("default  WIDTH=4 -> %b", p_default);
        $display("named    WIDTH=6 -> %b", p_override);
        $display("defparam WIDTH=8 -> %b", p_defparam);
        $display("hierarchical parameter value: %0d", u_override.WIDTH);
        $finish;
    end
endmodule
`default_nettype wire
