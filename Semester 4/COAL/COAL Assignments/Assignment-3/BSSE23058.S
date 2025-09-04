.data

all_students:       .asciz  "All Students: "
newline:            .asciz  "\n"
failed_student:     .asciz  "Failed Student(s): "
grade_output:       .asciz  "Grade Results: "
space:              .asciz  " "

    #all the students records strings stored in  the labels
student1:           .asciz  "Zunaira AbdulAziz BSSE23058 10 10 100 100 100 100"
student2:           .asciz  "Eashal Yasin BSSE23026 10 5 78 99 65 80"
student3:           .asciz  "Faiqa Arshad BSSE23028 6 9 88 67 6 90"
student4:           .asciz  "Fatima Khalid BSSE23104 9 8 91 82 49 76"
student5:           .asciz  "Fatima Noorulain BSSE23003 7 4 43 96 54 35"
student6:           .asciz  "Hamna Fatima BSSE23080 5 6 70 75 68 77"
student7:           .asciz  "Areeba Shahbaz BSSE23097 8 3 26 59 61 69"
student8:           .asciz  "Menahil Naeem BSSE23071 1 7 90 72 40 88"
student9:           .asciz  "Binish Ahsan BSSE23090 3 5 55 89 52 23"
student10:          .asciz  "Maleeka musadiq BSSE23106 0 0 0 0 0 0"

    #all the students records are stored in an array
students:
                    .word   student1
                    .word   student2
                    .word   student3
                    .word   student4
                    .word   student5
                    .word   student6
                    .word   student7
                    .word   student8
                    .word   student9
                    .word   student10
                    .word   0                                                   #like /n


    # Failed students array
failed_students:    .word   0, 0, 0, 0, 0, 0, 0, 0, 0, 0                        # Space for 10 students
failed_count:       .word   0

.text
                    .global _start

_start:

    #FOR PRINTING ALL STUDENTS
    la      a0,                 all_students                                    #load the address of the all_students string
    li      a7,                 4                                               #syscall for printing the string "All Students: "
    ecall

    #FOR PRINTING NEW LINE
    la      a0,                 newline                                         #load the address of the newline string
    li      a7,                 4                                               #printing the new line
    ecall

    #FOR PRINTING ALL STUDENTS
    la      t0,                 students                                        #load the address of the students array into

print_all_loop:


    lw      a0,                 0(t0)                                           #load the next student record
    beqz    a0,                 print_all_done                                  #if the last student is reached then exit the loop
    li      a7,                 4                                               # printing each student record one by one
    ecall

    #FOR PRINTING NEW LINE
    la      a0,                 newline                                         #load the address of the newline string
    li      a7,                 4                                               #printing the new line
    ecall

    #MOVING TO THE NEXT STUDENT
    addi    t0,                 t0,                 4                           #since words are 4 bytes, we add 4 to the address of the students array to get the address of the next student record

    j       print_all_loop

print_all_done:

    la      a0,                 newline
    li      a7,                 4
    ecall

    la      a0,                 grade_output                                    # Print "Grade Results:" header
    li      a7,                 4
    ecall

    la      a0,                 newline
    li      a7,                 4
    ecall

    # SECOND PART: CALCULATE AND PRINT GRADES # Initialize pointers
    la      t0,                 students                                        # t0: current student in main array
    la      t1,                 failed_students                                 # t1: failed students array
    sw      zero,               failed_count,       t2                          # Initialize failed count to 0

grading_loop:

    lw      s0,                 0(t0)                                           # Load next student record                                    # Load student record
    beqz    s0,                 print_failed_list

    # INITIALOZING VARIABLES FOR PROCESSING THE Marks
    li      s1,                 0                                               # S1: Space counter to track spaces in the student record
    li      s2,                 0                                               # S2: Current number being parsed (marks)
    li      s3,                 0                                               # S3: Mark counter to identify which mark is being processed
    li      s4,                 0                                               # S4: Total weighted marks for the student
    mv      s5,                 s0                                              # S5: Pointer to the current student record string

find_marks:

    lb      t2,                 0(s5)                                           # Load next character
    beqz    t2,                 process_marks

    li      t3,                 ' '                                             # Check if current character is space
    bne     t2,                 t3,                 next_char_mark              #If not space, continue

    addi    s1,                 s1,                 1                           # Found a space " " then increment space counter
    li      t3,                 3                                               # Marks start after 3 spaces (name, roll#)                    # Marks start after 3 spaces
    blt     s1,                 t3,                 next_char_mark              # If not at marks yet, continue

    # We're in marks section
    addi    s5,                 s5,                 1                           # Move past space
    li      s2,                 0                                               # Reset current number

parse_mark:

    # Parse the current mark digit by digit
    lb      t2,                 0(s5)
    beqz    t2,                 end_mark_parse

    li      t3,                 ' '
    beq     t2,                 t3,                 end_mark_parse              # End if space

    li      t3,                 10                                              #loading the newline character
    beq     t2,                 t3,                 end_mark_parse              # End if newline

    # Convert to digit and build number
    addi    t2,                 t2,                 -48                         # Convert from ASCII
    li      t3,                 10
    mul     s2,                 s2,                 t3                          # Multiply current by 10
    add     s2,                 s2,                 t2                          # Add new digit

    addi    s5,                 s5,                 1                           # Move to next character
    j       parse_mark

end_mark_parse:

    # We've parsed a complete mark - now apply weighting
    addi    s3,                 s3,                 1

    # Apply different weights based on which mark this is
    # The weights are:
    # Quiz 1 (5%): mark 1
    # Quiz 2 (5%): mark 2
    # Assignment 1 (10%): mark 3
    # Assignment 2 (10%): mark 4
    # Midterm (30%): mark 5
    # Final (40%): mark 6

    # Calculate weighted value
    li      t3,                 1
    beq     s3,                 t3,                 quiz1_weight                # Handle quiz 1
    li      t3,                 2
    beq     s3,                 t3,                 quiz2_weight                # Handle quiz 2
    li      t3,                 3
    beq     s3,                 t3,                 assign1_weight              # Handle assignment 1
    li      t3,                 4
    beq     s3,                 t3,                 assign2_weight              # Handle assignment 2
    li      t3,                 5
    beq     s3,                 t3,                 midterm_weight              # Handle midterm
    li      t3,                 6
    beq     s3,                 t3,                 final_weight                # Handle final

quiz1_weight:

    # Quiz 1 is out of 10, weighted at 5% of total
    li      t3,                 5                                               # Weight percentage
    mul     t4,                 s2,                 t3                          # Multiply mark by weight
    li      t3,                 10                                              # Out of 10
    div     t4,                 t4,                 t3                          # Calculate weighted value
    add     s4,                 s4,                 t4                          # Add to running total
    j       check_next_mark

quiz2_weight:

    # Same as quiz 1
    li      t3,                 5
    mul     t4,                 s2,                 t3
    li      t3,                 10
    div     t4,                 t4,                 t3
    add     s4,                 s4,                 t4
    j       check_next_mark

assign1_weight:

    # Assignment 1 is out of 100, weighted at 10%
    li      t3,                 10                                              # Weight percentage
    mul     t4,                 s2,                 t3                          # Multiply mark by weight
    li      t3,                 100                                             # Out of 100
    div     t4,                 t4,                 t3                          # Calculate weighted value
    add     s4,                 s4,                 t4                          # Add to running total
    j       check_next_mark

assign2_weight:

    # Same as assignment 1
    li      t3,                 10
    mul     t4,                 s2,                 t3
    li      t3,                 100
    div     t4,                 t4,                 t3
    add     s4,                 s4,                 t4
    j       check_next_mark

midterm_weight:

    # Midterm is out of 50, weighted at 30%
    li      t3,                 50                                              # Max possible score
    ble     s2,                 t3,                 midterm_normal              # If score <= 50, proceed
    mv      s2,                 t3                                              # Otherwise cap at 50

midterm_normal:

    li      t3,                 30                                              # Weight percentage
    mul     t4,                 s2,                 t3                          # Multiply mark by weight
    li      t3,                 50                                              # Out of 50
    div     t4,                 t4,                 t3                          # Calculate weighted value
    add     s4,                 s4,                 t4                          # Add to running total
    j       check_next_mark

final_weight:

    # Final is out of 100, weighted at 40%
    li      t3,                 40                                              # Weight percentage
    mul     t4,                 s2,                 t3                          # Multiply mark by weight
    li      t3,                 100                                             # Out of 100
    div     t4,                 t4,                 t3                          # Calculate weighted value
    add     s4,                 s4,                 t4                          # Add to running total

check_next_mark:

    # Check if we've processed all 6 marks
    li      t3,                 6
    blt     s3,                 t3,                 find_marks                  # If not, find next mark

process_marks:

    # Now we have the total weighted score - print student info and grade
    lw      a0,                 0(t0)                                           # Get student record again
    mv      s5,                 a0                                              # Copy pointer for printing

    # Print student name and roll number (stop at marks)
    li      s6,                 0                                               # Space counter

print_student_info:

    lb      a0,                 0(s5)                                           # Load next character
    beqz    a0,                 print_grade_info                                # If null, done

    # Check if we've reached the marks section (after 3 spaces)
    li      t3,                 ' '
    bne     a0,                 t3,                 print_char                  # If not space, print

    addi    s6,                 s6,                 1                           # Increment space counter
    li      t3,                 3
    beq     s6,                 t3,                 print_grade_info            # Stop after roll number

print_char:

    # Print the current character
    li      a7,                 11                                              # Print character syscall
    ecall
    addi    s5,                 s5,                 1                           # Move to next character
    j       print_student_info

print_grade_info:

    # Print a space for formatting
    la      a0,                 space
    li      a7,                 4
    ecall

    # Print the total weighted marks
    mv      a0,                 s4
    li      a7,                 1                                               # Print integer syscall
    ecall

    # Print another space
    la      a0,                 space
    li      a7,                 4
    ecall

    # Determine and print the letter grade
    li      t3,                 80
    bge     s4,                 t3,                 grade_A                     # A if >= 80
    li      t3,                 70
    bge     s4,                 t3,                 grade_B                     # B if >= 70
    li      t3,                 60
    bge     s4,                 t3,                 grade_C                     # C if >= 60
    li      t3,                 50
    bge     s4,                 t3,                 grade_D                     # D if >= 50

    # Grade F - store in failed students list
    li      a0,                 'F'
    # Store pointer to failed student
    lw      t3,                 failed_count                                    # Get current count
    slli    t4,                 t3,                 2                           # Multiply by 4 (word size)
    add     t5,                 t1,                 t4                          # Calculate address in array
    lw      t6,                 0(t0)                                           # Get current student pointer
    sw      t6,                 0(t5)                                           # Store in failed_students
    addi    t3,                 t3,                 1                           # Increment count
    sw      t3,                 failed_count,       t4                          # Store updated count
    j       print_grade

grade_A:

    li      a0,                 'A'
    j       print_grade

grade_B:

    li      a0,                 'B'
    j       print_grade

grade_C:

    li      a0,                 'C'
    j       print_grade

grade_D:

    li      a0,                 'D'

print_grade:

    # Print the letter grade
    li      a7,                 11                                              # Print character syscall
    ecall

    # Print newline after each student's grade
    la      a0,                 newline
    li      a7,                 4
    ecall

next_student:

    # Move to next student in array
    addi    t0,                 t0,                 4
    j       grading_loop

next_char_mark:

    # Helper jump for mark parsing
    addi    s5,                 s5,                 1
    j       find_marks

print_failed_list:

    # THIRD PART: PRINT FAILED STUDENTS

    # Check if there are any failed students
    lw      t3,                 failed_count
    beqz    t3,                 exit_program                                    # If none, exit

    # Print failed students header
    la      a0,                 newline
    li      a7,                 4
    ecall
    la      a0,                 failed_student
    li      a7,                 4
    ecall
    la      a0,                 newline
    li      a7,                 4
    ecall

    # Initialize pointers for printing failed students
    li      t4,                 0                                               # Counter
    la      t5,                 failed_students                                 # Pointer to array

print_failed_loop:

    bge     t4,                 t3,                 exit_program                # If done printing, exit

    # Load next failed student pointer
    lw      a0,                 0(t5)
    mv      s5,                 a0                                              # Copy for printing
    li      s6,                 0                                               # Space counter

print_failed_info:

    # Print student info up to roll number
    lb      a0,                 0(s5)
    beqz    a0,                 print_failed_done                               # If null, done

    # Check if we've reached marks section
    li      t6,                 ' '
    bne     a0,                 t6,                 print_failed_char           # If not space, print

    addi    s6,                 s6,                 1                           # Increment space counter
    li      t6,                 3
    beq     s6,                 t6,                 print_failed_done           # Stop after roll number

print_failed_char:

    # Print current character
    li      a7,                 11
    ecall
    addi    s5,                 s5,                 1                           # Move to next character
    j       print_failed_info

print_failed_done:

    # Print newline after each failed student
    la      a0,                 newline
    li      a7,                 4
    ecall

    # Move to next failed student
    addi    t4,                 t4,                 1                           # Increment counter
    addi    t5,                 t5,                 4                           # Move to next array element
    j       print_failed_loop

exit_program:

    # Exit the program
    li      a7,                 10                                              # Exit syscall
    ecall