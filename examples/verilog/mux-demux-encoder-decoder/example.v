`default_nettype none
module mux4 (
    input  wire [3:0] d,
    input  wire [1:0] sel,
    output wire       y
);
    assign y = d[sel];
endmodule

module dec2to4 (
    input  wire [1:0] a,
    input  wire       en,
    output wire [3:0] y
);
    assign y = en ? (4'b0001 << a) : 4'b0000;
endmodule

module demux1to4 (
    input  wire       d,
    input  wire [1:0] sel,
    output wire [3:0] y
);
    assign y = d ? (4'b0001 << sel) : 4'b0000;
endmodule

// Priority encoder written as dataflow equations: bit 3 wins.
module priority4 (
    input  wire [3:0] req,
    output wire       valid,
    output wire [1:0] code
);
    assign valid  = |req;
    assign code[1] = req[3] | req[2];
    assign code[0] = req[3] | (req[1] & ~req[2]);
endmodule
`default_nettype wire
