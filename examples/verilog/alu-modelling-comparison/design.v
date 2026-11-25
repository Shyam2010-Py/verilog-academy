`default_nettype none
// Two descriptions of the same 4-bit ALU.
module alu4_dataflow (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [1:0] op,
    output wire [3:0] y
);
    assign y = (op == 2'b00) ? (a & b)
             : (op == 2'b01) ? (a | b)
             : (op == 2'b10) ? (a + b)
             :                 (a - b);
endmodule

module alu4_behavioural (
    input  wire [3:0] a,
    input  wire [3:0] b,
    input  wire [1:0] op,
    output reg  [3:0] y
);
    always @* begin
        case (op)
            2'b00:   y = a & b;
            2'b01:   y = a | b;
            2'b10:   y = a + b;
            2'b11:   y = a - b;
            default: y = 4'b0000;
        endcase
    end
endmodule
`default_nettype wire
