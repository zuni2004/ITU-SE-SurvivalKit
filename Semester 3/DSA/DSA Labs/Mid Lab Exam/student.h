//
// Created by Zunaira on 08/10/2024.
//

#ifndef BSSE23058_STUDENT_H
#define BSSE23058_STUDENT_H

#include <iostream>
#include <algorithm>

using namespace std;

class Student {
private:
    string name;
    string rollNumber;
    const float *assignmentMarks;
    const float *quizMarks;
    float projectMarks;
    float midExamMarks;
    const float *finalExamMarks;
    float aggregate;
    Student *next;
public:
    Student(string name, string rollNumber);

    ~Student();

    void setNextStudent(Student *student);

    Student *getNextStudent();

    void inputMarks();

    void setAssignmentMarks(const float marks[5]);

    void setQuizMarks(const float marks[5]);

    void setProjectMarks(float marks);

    void setMidExamMarks(float marks);

    void setFinalExamMarks(const float marks[5]);

    void sortAssignments();

    void sortQuizzes();

    void calculateAggregate();

    float getAggregate();

    string getName();

    string getRollNumber();
};


#endif //BSSE23058_STUDENT_H
