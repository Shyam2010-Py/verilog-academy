`default_nettype none
`timescale 1ns / 1ps

// One full adder is reused four times. carry[0] leaves bit 0, carry[3]
// leaves bit 3 and becomes the unsigned carry-out.
module full_adder (
    input  wire a,
    input  wire b,
    input  wire cin,
    output wire sum,
    output wire carry
);

    assign sum   = a ^ b ^ cin;
    assign carry = (a & b) | (cin & (a ^ b));

endmodule

module four_bit_adder (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire       cin,
    output wire [3:0] sum,
    output wire       cout,
    output wire       overflow
);

    wire [3:0] carry;

    full_adder fa0 (.a(a[0]), .b(b[0]), .cin(cin),     .sum(sum[0]), .carry(carry[0]));
    full_adder fa1 (.a(a[1]), .b(b[1]), .cin(carry[0]), .sum(sum[1]), .carry(carry[1]));
    full_adder fa2 (.a(a[2]), .b(b[2]), .cin(carry[1]), .sum(sum[2]), .carry(carry[2]));
    full_adder fa3 (.a(a[3]), .b(b[3]), .cin(carry[2]), .sum(sum[3]), .carry(carry[3]));

    assign cout     = carry[3];
    assign overflow = carry[2] ^ carry[3];

endmodule

`default_nettype wire
