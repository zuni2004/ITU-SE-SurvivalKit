module twoto1(input A,input B,input sel,output out);
wire ns,and1,and2;
not G1(ns,sel);
and G2(and1,ns,A);
and G3(and2,sel,B);
or G4(out,and1,and2);
endmodule
module fourto1(input [3:0] s1,input  [1:0]sel,output reg  out);
always @(*) begin
    case(sel)
    2'b00:out=s1[0];
        2'b01:out=s1[1];
    2'b10:out=s1[2];
    2'b11:out=s1[3];


    endcase
end
endmodule
module eightto1(input[7:0]I,input[2:0]s,output  out);
wire out1,out2;
fourto1 f1(.s1(I[3:0]),.sel(s[1:0]),.out(out1));
fourto1 f2(.s1(I[7:4]),.sel(s[1:0]),.out(out2));
twoto1 f3(.A(out1),.B(out2),.sel(s[2]),.out(out));
// if use only 4 to 1
//fourto1 f3(.s1({2'b00,out1,out2}),.sel({s[2],1'b0}),.out(out));
//fourto1 f3(.s1({out1,out2,out1,out2}),.sel({s[2],s[2]}),.out(out));

endmodule
module min147(input A,input B,input C,output  F);
 wire [7:0] mux_inputs;
    
    // Assign MUX inputs based on minterms 1, 4, and 7
    assign mux_inputs[0] = 1'b0; // m(0)
    assign mux_inputs[1] = 1'b1; // m(1)
    assign mux_inputs[2] = 1'b0; // m(2)
    assign mux_inputs[3] = 1'b0; // m(3)
    assign mux_inputs[4] = 1'b1; // m(4)
    assign mux_inputs[5] = 1'b0; // m(5)
    assign mux_inputs[6] = 1'b0; // m(6)
    assign mux_inputs[7] = 1'b1; // m(7)
    
    // Instantiate the 8-to-1 MUX and connect inputs
    eightto1 my_mux(.I(mux_inputs), .s({A, B, C}), .out(F));
endmodule