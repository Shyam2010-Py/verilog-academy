`default_nettype none
// A four-iteration loop that synthesis unrolls into adders.
module popcount4 (
    input  wire [3:0] d,
    output reg  [2:0] count
);
    integer i;

    always @* begin
        count = 3'd0;
        for (i = 0; i < 4; i = i + 1)
            count = count + d[i];
    end
endmodule

// The loop drives each output bit from a different input bit.
module reverse8 (
    input  wire [7:0] d,
    output reg  [7:0] q
);
    integer i;

    always @* begin
        for (i = 0; i < 8; i = i + 1)
            q[i] = d[7 - i];
    end
endmodule
`default_nettype wire
