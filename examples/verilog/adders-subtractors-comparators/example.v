`default_nettype none
// Addition and subtraction share one adder; sub inverts B and adds 1.
module addsub4 (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire       sub,
    output wire [3:0] sum,
    output wire       cout,
    output wire       zero,
    output wire       overflow
);
    wire [3:0] bx = b ^ {4{sub}};
    wire [4:0] wide = {1'b0, a} + {1'b0, bx} + sub;

    assign sum      = wide[3:0];
    assign cout     = wide[4];
    assign zero     = (sum == 4'b0000);
    assign overflow = (a[3] & bx[3] & ~sum[3]) |
                      (~a[3] & ~bx[3] & sum[3]);
endmodule

module comparator4 (
    input  wire [3:0] a,
    input  wire [3:0] b,
    output wire       lt,
    output wire       eq,
    output wire       gt
);
    assign lt = (a < b);
    assign eq = (a == b);
    assign gt = (a > b);
endmodule

// The same comparison with signed ports: the bits are identical to
// comparator4, but the interpretation of bit 3 is different.
module comparator4_signed (
    input  wire signed [3:0] a,
    input  wire signed [3:0] b,
    output wire              lt,
    output wire              eq,
    output wire              gt
);
    assign lt = (a < b);
    assign eq = (a == b);
    assign gt = (a > b);
endmodule
`default_nettype wire
