`default_nettype none
// Same priority encoder, two ways.
module prio_if (
    input  wire [3:0] req,
    output reg  [1:0] code,
    output reg        valid
);
    always @* begin
        valid = 1'b1;
        if      (req[3]) code = 2'd3;
        else if (req[2]) code = 2'd2;
        else if (req[1]) code = 2'd1;
        else if (req[0]) code = 2'd0;
        else begin
            code  = 2'd0;
            valid = 1'b0;
        end
    end
endmodule

module prio_casez (
    input  wire [3:0] req,
    output reg  [1:0] code,
    output reg        valid
);
    always @* begin
        valid = |req;
        casez (req)
            4'b1???: code = 2'd3;
            4'b01??: code = 2'd2;
            4'b001?: code = 2'd1;
            4'b0001: code = 2'd0;
            default: code = 2'd0;
        endcase
    end
endmodule

// Deliberate latch: q is not assigned on every path.
module latch_risk (
    input  wire en,
    input  wire d,
    output reg  q
);
    always @* begin
        if (en)
            q = d;
    end
endmodule
`default_nettype wire
