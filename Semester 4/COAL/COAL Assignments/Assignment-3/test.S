# Macro definitions MUST come before any data or text sections
.macro print_str str_label
    li a7, 64
    li a0, 1
    la a1, str_label
    ecall
.endm # Added missing .endm

.macro atoi buff
    la t2, endl
    lb t3, 0(t2)

    li t6, 0
    li t5, 10
    la t2, buff

loop_atoi:
    lb t4, 0(t2)
    beq t4, t3, end_atoi
    addi t4, t4, -48
    mul t6, t6, t5
    add t6, t6, t4
    addi t2, t2, 1
    j loop_atoi

end_atoi:
.endm

.macro read_char fd, byte
    # read(fd,buffer,1)
    li a7, 63
    mv a0, fd
    la a1, byte
    li a2, 1
    ecall
.endm

.macro write_char fd, byte
    #write(fd,char,1)
    li a7, 64
    mv a0, fd
    la a1, byte
    li a2, 1
    ecall
.endm

.data
    char: .space 1

.section .rodata
    endl:
        .asciz "\n"
    endl_end:
    A:
        .ascii "A"
    A_end:
    B:
        .ascii "B"
    B_end:
    C:
        .ascii "C"
    C_end:
    D:
        .ascii "D"
    D_end:
    F:
        .ascii "F"
    F_end:

    filename: .asciz "input.txt"
    outfilename: .asciz "output.txt"

.text
.globl _start
_start:
    # open the input file
    li a7, 56
    li a0, -100
    la a1, filename
    li a2, 0
    ecall
    bltz a0, e
    mv s0, a0

    # open the output file
    li a7, 56
    li a0, -100
    la a1, outfilename
    li a2, 1026
    ecall
    bltz a0, e
    mv s1, a0

    li s8, 32

main_loop:
fname_loop:
    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    beq t1, s8, f_name_done
    write_char s1, char
    j fname_loop
f_name_done:
    write_char s1, char

lname_loop:
    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    beq t1, s8, l_name_done
    write_char s1, char
    j lname_loop
l_name_done:
    write_char s1, char

reg_loop:
    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    beq t1, s8, reg_done
    write_char s1, char
    j reg_loop
reg_done:
    write_char s1, char

# marks processing
li s3, 20
li s4, 10
q1_marks_loop:
    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    beq t1, s8, q1_marks_done
    atoi char
    j q1_marks_loop
q1_marks_done:
    mv s2, t6

q2_marks_loop:
    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    beq t1, s8, q2_marks_done
    atoi char
    j q2_marks_loop
q2_marks_done:
    add s2, s2, t6
    div s2, s2, s3
    mul s9, s2, s4

    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    atoi char
    mul s2, t6, s4
    read_char s0, char
    blez a0, e
    atoi char
    add s2, s2, t6
    read_char s0, char
    blez a0, e
    beq t1, s8, assg1_marks_done
assg1_marks_done:

    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    atoi char
    mul s3, t6, s4
    read_char s0, char
    blez a0, e
    atoi char
    add s3, s3, t6
    read_char s0, char
    blez a0, e
    beq t1, s8, assg2_marks_done
assg2_marks_done:
    add s2, s2, s3
    li s3, 200
    li s5, 20
    div s2, s2, s3
    mul s2, s2, s5
    add s9, s9, s2

    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    atoi char
    mul s2, t6, s4
    read_char s0, char
    blez a0, e
    atoi char
    add s2, s2, t6
    read_char s0, char
    blez a0, e
    beq t1, s8, mid_marks_done
mid_marks_done:
    li s3, 50
    li s5, 30
    div s2, s2, s3
    mul s2, s2, s5
    add s9, s9, s2

    read_char s0, char
    blez a0, e
    la t0, char
    lb t1, 0(t0)
    atoi char
    mul s2, t6, s4
    read_char s0, char
    blez a0, e
    atoi char
    add s2, s2, t6
    read_char s0, char
    blez a0, e
    beq t1, s8, final_marks_done
final_marks_done:
    li s3, 100
    li s5, 40
    div s2, s2, s3
    mul s2, s2, s5
    add s9, s9, s2

    la t0,char
    sb s8,0(t0)
    write_char s1, char

    li s2, 50
    li s3, 60
    li s4, 70
    li s5, 80
    li s6, 59
    li s7, 69
    li s8, 79

    blez a0, e

    blt s9, s2, F
    bge s9, s2, D
    bge s9, s3, C
    bge s9, s4, B
    bge s9, s5, A

A:
    li t0, 65
    la t1, char
    sb t0, 0(t1)
    write_char s1, char
    j end_grade
B:
    bgt s9, s8, A
    li t0, 66
    la t1, char
    sb t0, 0(t1)
    write_char s1, char
    j end_grade
C:
    bgt s9, s7, B
    bgt s9, s8, A
    li t0, 67
    la t1, char
    sb t0, 0(t1)
    write_char s1, char
    j end_grade
D:
    bgt s9, s6, C
    bgt s9, s7, B
    bgt s9, s8, A
    li t0, 68
    la t1, char
    sb t0, 0(t1)
    write_char s1, char
    j end_grade
F:
    li t0, 70
    la t1, char
    sb t0, 0(t1)
    write_char s1, char
end_grade:

    li a7, 64
    li a0, 1
    la a1, endl
    li a2, 1
    ecall

    li a7, 57
    mv a0, s0
    ecall

e:
    li a7, 93
    li a0, 0
    ecall
