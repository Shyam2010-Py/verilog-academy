`default_nettype none
// Two leaf cells with identical ports.
module and2 (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a & b;
endmodule

module or2 (
    input  wire a,
    input  wire b,
    output wire y
);
    assign y = a | b;
endmodule

// One level of hierarchy. Named connections make the mapping explicit.
module logic_pair (
    input  wire a,
    input  wire b,
    output wire y_and,
    output wire y_or
);
    and2 u_and (.a(a), .b(b), .y(y_and));
    or2  u_or  (.a(a), .b(b), .y(y_or));
endmodule
`default_nettype wire
