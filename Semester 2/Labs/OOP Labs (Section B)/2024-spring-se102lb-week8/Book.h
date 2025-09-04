//
// Created by saleha bilal on 19/03/2024.
//

#ifndef UNTITLED4_BOOK_H
#define UNTITLED4_BOOK_H
#include <iostream>
#include <string>
#include <vector>
using namespace std;

class Book {
    string title;
    bool available;
public:
    Book();
    Book(const string& t);
    const string& getTitle()const;
    bool isAvailable()const;
    void borrowBook();
    void returnBook();
    friend ostream& operator<<(ostream& os, const Book& book);
    friend istream& operator>>(istream& is, Book& book);
};


#endif //UNTITLED4_BOOK_H
