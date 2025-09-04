//
// Created by saleha bilal on 19/03/2024.
//

#ifndef UNTITLED4_LIBRARY_H
#define UNTITLED4_LIBRARY_H
using namespace std;
#include <iostream>
#include <vector>
#include "Book.h"
const int MAX_BOOKS=10;

class Library {
    static Library *instance;
//    vector<Book> books;
Book *books[MAX_BOOKS];
int numBooks;
Library();
public:
    static Library *getInstance();
    void addBooks(const Book& book);
    void removeBooks(const Book& book);
    void displayBooks()const;
    Book* findBook(const string& title);
};


#endif //UNTITLED4_LIBRARY_H
