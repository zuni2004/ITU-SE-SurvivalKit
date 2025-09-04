//
// Created by Zunaira on 08/10/2024.
//

#include "student_linked_list.h"

StudentLinkedList::StudentLinkedList() {
    head = nullptr;
    tail = nullptr;
    count = 0;
}

StudentLinkedList::~StudentLinkedList() {
    Student *position = head; //points a pointer to the head
    while (position != nullptr) {//traverse till the end of list
        Student *next = position->getNextStudent();//point a new pointer to the next node
        delete next; //delete that node
        next = position;//point to the next node
        next = nullptr;
    }
    position = nullptr;
}

void StudentLinkedList::addStudent(string name, string roll_number) {
    Student *student = new Student(name, roll_number); //makes a new node, initializes the name and rollnumber
    student->setNextStudent(nullptr);//setting the next node to nullptr
    student->inputMarks();//taking input of marks and then assigning to the respective domain in the student class
    student->calculateAggregate(); //calculates the aggreagte by the given marks and then sets the aggregate for the student
    if (head == nullptr) {//checks if list is empty
        head = student; //assigns head to student
        tail = student;//assigns tail to student
        student = nullptr;//so no dangling pointer is there
    } else {
        tail->setNextStudent(student);//if not empty then assign the tail to the student new node
        tail = student; //points to that new node the tail
        student = nullptr; //no dangling pointer
    }
    count++;//increments the count
}

Student *StudentLinkedList::getStudent(string rollNumber) {
    Student *postion = head;//make a pointer and point it to head
    while (postion->getNextStudent() != nullptr) { //traverse until the end of the list
        if (postion->getRollNumber() == rollNumber) { //checks for the respective roll number
            return postion; //if found return the node
        } else {
            postion = postion->getNextStudent();//if not point to next student
        }
    }
    return nullptr;// if not found return nullptr
}

void StudentLinkedList::inputMarks(string roll_number) {
    getStudent(roll_number)->inputMarks();
}

void StudentLinkedList::inputMarksforAll() {
//    inputMarks();
}

void StudentLinkedList::calculateAggregates() {
    Student *student;
    student->calculateAggregate();
}

void StudentLinkedList::sortStudentsByAggregate() {
    for (int i = 0; i < count - 1; i++) {
        int min = i;
        for (int j = 1 + i; j < count; ++j) {

        }
    }
}

void StudentLinkedList::displayStudents() {
    Student *position = head;//points a new pointer to head
    while (position->getNextStudent() != nullptr) {//traverse until end
        cout << "Name: " << position->getName() << "\nRoll Number: " << position->getRollNumber() << endl;
    }
    cout << endl;
    position = nullptr;//no dangling pointer
}

float StudentLinkedList::getAggregate(string roll_number) {
    Student *position = head;//points a new pointer to head
    while (position->getNextStudent() != nullptr) {//traverse till the next student
        if (position->getRollNumber() == roll_number) { //checks for the roll number
            return getAggregate(roll_number); //if found return the aggregate for the roll number
        } else {
            position = position->getNextStudent();//if not move to the next node
        }
    }
    return 0;
}
