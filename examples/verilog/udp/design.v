`default_nettype none
// Combinational UDP: a 2:1 multiplexer as a truth table.
primitive mux2_udp (out, sel, a, b);
    output out;
    input  sel, a, b;
    table
        // sel a b : out
           0  0 ? : 0;
           0  1 ? : 1;
           1  ? 0 : 0;
           1  ? 1 : 1;
    endtable
endprimitive

// Level-sensitive sequential UDP: a transparent D latch.
primitive dlatch_udp (q, en, d);
    output q;
    reg    q;
    input  en, d;
    table
        // en  d : q : q+
           1   0 : ? : 0;
           1   1 : ? : 1;
           0   ? : ? : -;
    endtable
endprimitive
`default_nettype wire
