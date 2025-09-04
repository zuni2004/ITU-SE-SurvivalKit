//
// Created by Zunaira on 08/10/2024.
//

#include "student.h"

Student::Student(string name, string rollNumber) : name(name), rollNumber(rollNumber), next(nullptr) {

}

Student::~Student() {

}

void Student::setNextStudent(Student *student) { //setter for the next student node
    next = student;
}

Student *Student::getNextStudent() { //getting the next node
    return next;
}

void Student::inputMarks() {
    float *assignmentArray = new float[5]; //dynamically makes 5 float array and then takes input
    for (int i = 0; i < 5; i++) {
        cout << "Enter Assignment " << i + 1 << " Marks: ";
        cin >> assignmentArray[i];
    }
    setAssignmentMarks(assignmentArray);//sets the assignment marks
    float *quizzesArray = new float[5];
    for (int i = 0; i < 5; i++) {
        cout << "Enter Quiz " << i + 1 << " Marks: ";
        cin >> quizzesArray[i];
    }
    setQuizMarks(quizMarks);
    cout << "Enter Project Marks: ";
    cin >> projectMarks;
    setProjectMarks(projectMarks);
    cout << "Enter Mid Exam Marks: ";
    cin >> midExamMarks;
    setMidExamMarks(midExamMarks);
    float *finalMarksArray = new float[5];
    for (int i = 0; i < 5; i++) {
        cout << "Enter Final Question " << i + 1 << " Marks: ";
        cin >> finalMarksArray[i];
    }
    setFinalExamMarks(finalExamMarks);
}

void Student::setAssignmentMarks(const float *marks) {//setting the marks
    assignmentMarks = marks;
}

void Student::setQuizMarks(const float *marks) {
    quizMarks = marks;
}

void Student::setProjectMarks(float marks) {
    projectMarks = marks;
}

void Student::setMidExamMarks(float marks) {
    midExamMarks = marks;
}

void Student::setFinalExamMarks(const float *marks) {
    finalExamMarks = marks;
}

void
Student::sortAssignments() {//sorting the assignment marks but i dont know why the temp is not being assigned to the assignment
    for (int i = 0; i < 4; i++) {
        for (int j = 1 + i; j < 5; ++j) {
            if (assignmentMarks[i] < assignmentMarks[j]) {
//                int temp = assignmentMarks[j];
//                assignmentMarks[j] = assignmentMarks[i];
//                assignmentMarks[i] = temp;
            }
        }
    }
}

void Student::sortQuizzes() {
    for (int i = 0; i < 4; i++) {
        for (int j = 1 + i; j < 5; ++j) {
//            if (quizMarks[i] < quizMarks[j]) {
//                int temp = quizMarks[j];
//                quizMarks[j] = quizMarks[i];
//                quizMarks[i] = temp;
//            }
        }
    }
}

void Student::calculateAggregate() {
    float totalAssignmentMarks = 0, totalQuizzesMark = 0, totalFinalMarks = 0;
    for (int i = 0; i < 4; ++i) {
        totalAssignmentMarks += assignmentMarks[i];
    }
    for (int i = 0; i < 4; ++i) {
        totalQuizzesMark += quizMarks[i];
    }
    float perAss, perQuiz, project, perMid, perFinal[5], totalFinalPerce;
    for (int i = 1; i <= 5; ++i) {
        if (i == 1) {
            perFinal[i - 1] = finalExamMarks[i - 1] / 30 * 100;
            perFinal[i - 1] = perFinal[i - 1] * 15 / 100;
        } else if (i == 2) {
            perFinal[i - 1] = finalExamMarks[i - 1] / 30 * 100;
            perFinal[i - 1] = perFinal[i - 1] * 10 / 100;
        } else if (i == 3) {
            perFinal[i - 1] = finalExamMarks[i - 1] / 30 * 100;
            perFinal[i - 1] = perFinal[i - 1] * 25 / 100;
        } else if (i == 4) {
            perFinal[i - 1] = finalExamMarks[i - 1] / 30 * 100;
            perFinal[i - 1] = perFinal[i - 1] * 30 / 100;
        } else if (i == 5) {
            perFinal[i - 1] = finalExamMarks[i - 1] / 30 * 100;
            perFinal[i - 1] = perFinal[i - 1] * 20 / 100;
        }
    }
    for (int i = 0; i < 5; ++i) {
        totalFinalPerce += perFinal[i];
    }
    project = projectMarks * 15 / 100;
    perAss = totalAssignmentMarks * 10 / 100;
    perQuiz = totalQuizzesMark * 100 / 40;
    perQuiz = perQuiz * 15 / 100;
    perMid = midExamMarks * 25 / 100;
    totalFinalPerce = totalFinalPerce * 45 / 100;
    float TotalAggregate = perQuiz + perAss + perMid + project + totalFinalPerce;
    aggregate = TotalAggregate;
}

float Student::getAggregate() {
    return aggregate;
}

string Student::getName() {
    return name;
}

string Student::getRollNumber() {
    return rollNumber;
}
