//
// Created by Zunaira on 08/10/2024.
//

#ifndef BSSE23058_STUDENT_LINKED_LIST_H
#define BSSE23058_STUDENT_LINKED_LIST_H

#include <iostream>

using namespace std;

#include "student.h"

class StudentLinkedList {
private:
    Student *head, *tail;
    int count;
public:
    StudentLinkedList();

    ~StudentLinkedList();

    void addStudent(string name, string roll_number);

    void inputMarks(string roll_number);

    void inputMarksforAll();

    Student *getStudent(string rollNumber);

    void calculateAggregates();

    void sortStudentsByAggregate();

    void displayStudents();

    float getAggregate(string roll_number);
};


#endif //BSSE23058_STUDENT_LINKED_LIST_H
