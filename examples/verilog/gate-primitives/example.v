`default_nettype none
// Primitive gates: outputs first, then inputs.
module gate_demo (
    input  wire a,
    input  wire b,
    output wire y_and,
    output wire y_or,
    output wire y_xor,
    output wire y_nand,
    output wire y_nor,
    output wire y_not,
    output wire y_tri
);
    and  g_and  (y_and, a, b);
    or   g_or   (y_or, a, b);
    xor  g_xor  (y_xor, a, b);
    nand g_nand (y_nand, a, b);
    nor  g_nor  (y_nor, a, b);
    not  g_not  (y_not, a);
    bufif1 g_tri (y_tri, a, b);
endmodule
`default_nettype wire
