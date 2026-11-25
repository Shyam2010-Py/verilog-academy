`default_nettype none
// Blocking assignments run immediately, in source order.
module shift_blocking (
    input  wire clk,
    input  wire d,
    output reg  q0,
    output reg  q1,
    output reg  q2
);
    always @(posedge clk) begin
        q0 = d;
        q1 = q0;
        q2 = q1;
    end
endmodule

// Non-blocking assignments sample every right-hand side first.
module shift_nonblocking (
    input  wire clk,
    input  wire d,
    output reg  q0,
    output reg  q1,
    output reg  q2
);
    always @(posedge clk) begin
        q0 <= d;
        q1 <= q0;
        q2 <= q1;
    end
endmodule
`default_nettype wire
