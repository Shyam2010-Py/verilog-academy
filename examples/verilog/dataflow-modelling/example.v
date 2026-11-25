`default_nettype none
// Every output is a continuous function of the inputs.
module mux4 (
    input  wire [3:0] d,
    input  wire [1:0] sel,
    output wire       y
);
    assign y = sel[1] ? (sel[0] ? d[3] : d[2])
                      : (sel[0] ? d[1] : d[0]);
endmodule

module mux4_tb;
    reg  [3:0] d;
    reg  [1:0] sel;
    wire       y;
    integer i;

    mux4 dut (.d(d), .sel(sel), .y(y));

    initial begin
        d = 4'b1010;
        $display("d=%b", d);
        $display("sel | y");
        $display("----+--");
        for (i = 0; i < 4; i = i + 1) begin
            sel = i[1:0];
            #1;
            $display(" %b  | %b", sel, y);
        end
        $finish;
    end
endmodule
`default_nettype wire
