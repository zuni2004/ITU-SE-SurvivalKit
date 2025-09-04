//
// Created by Zunaira on 08/10/2024.
//
#include <iostream>
#include "student_linked_list.h"

using namespace std;

int main() {
//    cout << "HELLO WORLD\n";
//    cout << "Adding a student\n";
//    int choice;
//    do {
//        cout << "1. Add a Student\n";
//        cout << "2. Display Student\n";
//        cout << "3. Exit\n";
//
//    } while (choice != 3);
    StudentLinkedList *studentLinkedList = new StudentLinkedList();
    studentLinkedList->addStudent("Zuni", "BSSE23058");
    studentLinkedList->displayStudents();
    delete studentLinkedList;
    return 0;
}