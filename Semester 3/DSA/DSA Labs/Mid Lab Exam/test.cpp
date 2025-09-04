#define CATCH_CONFIG_MAIN  // This tells Catch to provide a main() - only do this in one cpp file
#include "catch.hpp"
#include "student_linked_list.h"

TEST_CASE("Test Case Task 1") {
    StudentLinkedList classList;

    // Adding students
    classList.addStudent("Saad Ali", "123");
    classList.addStudent("Kashif Ahmed", "456");

    // Directly setting marks for student "123"
    float assignmentMarks123[5] = {90, 80, 85, 75, 95};
    float quizMarks123[5] = {8, 9, 10, 7, 6};
    float finalExamMarks123[5] = {25, 20, 28, 30, 25};
    classList.getStudent("123")->setAssignmentMarks(assignmentMarks123);
    classList.getStudent("123")->setQuizMarks(quizMarks123);
    classList.getStudent("123")->setProjectMarks(85);
    classList.getStudent("123")->setMidExamMarks(78);
    classList.getStudent("123")->setFinalExamMarks(finalExamMarks123);

    // Directly setting marks for student "456"
    float assignmentMarks456[5] = {88, 92, 79, 85, 91};
    float quizMarks456[5] = {9, 10, 8, 7, 9};
    float finalExamMarks456[5] = {28, 27, 30, 26, 29};
    classList.getStudent("456")->setAssignmentMarks(assignmentMarks456);
    classList.getStudent("456")->setQuizMarks(quizMarks456);
    classList.getStudent("456")->setProjectMarks(90);
    classList.getStudent("456")->setMidExamMarks(82);
    classList.getStudent("456")->setFinalExamMarks(finalExamMarks456);

    // Calculate aggregates for all students
    classList.calculateAggregates();

    // Test case for getting aggregate by roll number
    REQUIRE(classList.getAggregate("123") == 93);  // Expected aggregate for "123"
    REQUIRE(classList.getAggregate("456") == 98);  // Expected aggregate for "456"
}




