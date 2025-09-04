//
// Created by saleha bilal on 19/03/2024.
//

#include "User.h"


User::User(const string &n) : name(n){

}

void User::borrowBook(Book &book) {
    book.borrowBook();
}

void User::returnBook(Book &book) {
    book.returnBook();
}

const string &User::getName() const {
    return name;
}