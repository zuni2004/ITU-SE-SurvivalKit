#include "Library.h"
#include <iostream>
#include "Library.h"

#include <vector>

 Library *Library::instance= nullptr;

 Library::Library() :numBooks(0) {

}

Library *Library::getInstance() {
     if(!instance){
         instance=new Library();
     }
    return instance;
 }

void Library::addBooks(const Book &book) {
    if (numBooks < MAX_BOOKS)
        books[numBooks++] = new Book(book);
    else
        cout << "Library is full. Cannot add more books." << endl;
 }


void Library::removeBooks(const Book &book) {
    for (int i = 0; i < numBooks; ++i) {
        if (books[i]->getTitle() == book.getTitle()) {
            delete books[i];
            for (int j = i; j < numBooks - 1; ++j)
                books[j] = books[j + 1];
            numBooks--;
            cout << "Book removed successfully." << endl;
            return;
        }
    }
    cout << "Book not found in the library." << endl;
//    books[numBooks--]=new Book(book);
 }

void Library::displayBooks() const {
    cout << "Books available in the library:" << endl;
    for (int i = 0; i < numBooks; ++i)
        cout << *books[i] << endl;
 }

Book *Library::findBook(const string &title) {
    for (int i = 0; i < numBooks; ++i) {
        if (books[i]->getTitle() == title)
            return books[i];
    }
    return nullptr;
 }