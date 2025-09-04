//
// Created by saleha bilal on 19/03/2024.
//

#include "Admin.h"

void Admin::addBookToLibrary(const Book& book){
    Library::getInstance()->addBooks(book);
}

void Admin::removeBookFromLibrary(const string& title){
    Library::getInstance()->removeBooks(title);
}

