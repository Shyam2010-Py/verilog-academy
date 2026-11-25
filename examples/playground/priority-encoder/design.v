`default_nettype none
`timescale 1ns / 1ps

// Highest-numbered request wins. valid is low only when no request is high.
module priority_encoder_4_to_2 (
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

`default_nettype wire
