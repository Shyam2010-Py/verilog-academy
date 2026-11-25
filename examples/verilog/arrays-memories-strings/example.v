`default_nettype none
// A memory is an array of words, not one wide vector.
module arrays_tb;
    reg [7:0] mem [0:3];
    reg [8*5-1:0] label;
    integer i;

    initial begin
        label = "HELLO";

        for (i = 0; i < 4; i = i + 1) begin
            mem[i] = 8'h10 + i[7:0];
        end

        $display("label          = %0s", label);

        for (i = 0; i < 4; i = i + 1) begin
            $display("mem[%0d]         = %h", i, mem[i]);
        end

        $display("mem[2][3]      = %b", mem[2][3]);
        $display("mem[2][7:4]    = %h", mem[2][7:4]);
        $display("whole memory is not one vector; read word by word");
        $finish;
    end
endmodule
`default_nettype wire
