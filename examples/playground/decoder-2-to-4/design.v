`default_nettype none
`timescale 1ns / 1ps

// A 2-to-4 decoder with an active-high enable. Disabled means all low.
module decoder_2_to_4 (
    input  wire       enable,
    input  wire [1:0] addr,
    output reg  [3:0] y
);

    always @* begin
        if (!enable)
            y = 4'b0000;
        else begin
            case (addr)
                2'b00: y = 4'b0001;
                2'b01: y = 4'b0010;
                2'b10: y = 4'b0100;
                2'b11: y = 4'b1000;
                default: y = 4'b0000;
            endcase
        end
    end

endmodule

`default_nettype wire
