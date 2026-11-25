`timescale 1ns / 1ps
`default_nettype none
// Nets, variables, vectors and the four-valued data model.
module data_types_tb;
    wire [7:0] bus;
    reg  [3:0] nibble;
    reg  [7:0] byte_reg;
    integer    count;
    real       voltage;
    time       stamp;

    assign bus = 8'hA5;

    initial begin
        nibble   = 4'b1010;
        byte_reg = 8'b0000_1111;
        count    = -3;
        voltage  = 1.8;

        #5;
        stamp = $time;

        $display("bus (wire)        = %b  %h", bus, bus);
        $display("nibble (reg)      = %b", nibble);
        $display("byte_reg (reg)    = %b", byte_reg);
        $display("count (integer)   = %0d", count);
        $display("voltage (real)    = %0.2f", voltage);
        $display("stamp (time)      = %0t", stamp);
        $display("part-select [7:4] = %b", bus[7:4]);
        $display("bit-select  [0]   = %b", bus[0]);
        $finish;
    end
endmodule
`default_nettype wire
