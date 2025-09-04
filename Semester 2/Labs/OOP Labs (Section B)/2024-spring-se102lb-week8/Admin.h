//
// Created by saleha bilal on 19/03/2024.
//

#ifndef UNTITLED4_ADMIN_H
#define UNTITLED4_ADMIN_H
#include <iostream>
using namespace std;
#include "Book.h"
#include "Library.h"

class Admin {
public:
    static void addBookToLibrary(const Book& book);
    static void removeBookFromLibrary(const string& title);
};


#endif //UNTITLED4_ADMIN_H
