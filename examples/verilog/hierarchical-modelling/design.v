`default_nettype none
// Leaf cell: one-bit full adder built from primitive gates.
module full_adder (
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire cout
);
    wire s1;
    wire c1;
    wire c2;

    xor x1 (s1, a, b);
    xor x2 (sum, s1, cin);
    and a1 (c1, a, b);
    and a2 (c2, s1, cin);
    or  o1 (cout, c1, c2);
endmodule

// Four leaf cells composed into a ripple-carry adder.
module rca4 (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire       cin,
    output wire [3:0] sum,
    output wire       cout
);
    wire c1;
    wire c2;
    wire c3;

    full_adder fa0 (.a(a[0]), .b(b[0]), .cin(cin), .sum(sum[0]), .cout(c1));
    full_adder fa1 (.a(a[1]), .b(b[1]), .cin(c1),  .sum(sum[1]), .cout(c2));
    full_adder fa2 (.a(a[2]), .b(b[2]), .cin(c2),  .sum(sum[2]), .cout(c3));
    full_adder fa3 (.a(a[3]), .b(b[3]), .cin(c3),  .sum(sum[3]), .cout(cout));
endmodule
`default_nettype wire
