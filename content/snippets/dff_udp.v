// Language reference only: Icarus Verilog 13.0 compiles this primitive but
// does not evaluate its edge-sensitive table, so the output stays x.
primitive dff_udp (q, clk, d);
    output q;
    reg    q;
    input  clk, d;
    table
        // clk   d : q : q+
           (01)  0 : ? : 0;   // rising edge, data 0
           (01)  1 : ? : 1;   // rising edge, data 1
           (?0)  ? : ? : -;   // falling edge: hold
           (??)  ? : ? : -;   // any other change: hold
    endtable
endprimitive
