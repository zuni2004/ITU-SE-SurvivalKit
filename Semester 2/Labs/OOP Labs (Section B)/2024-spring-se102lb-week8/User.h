//
// Created by saleha bilal on 19/03/2024.
//

#ifndef UNTITLED4_USER_H
#define UNTITLED4_USER_H
#include "Library.h"

class User {
    string name;
public:
    User(const string& n);
    void borrowBook(Book& book);
    void returnBook(Book& book);
    const string& getName() const;
};


#endif //UNTITLED4_USER_H
