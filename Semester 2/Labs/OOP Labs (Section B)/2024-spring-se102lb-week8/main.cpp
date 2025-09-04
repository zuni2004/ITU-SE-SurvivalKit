#include <iostream>
#include <string>
using namespace std;

#include "Book.h"
#include "Library.h"
#include "User.h"
#include "Admin.h"

int main() {
    int choice;
    cin>>choice;
    Library *library=Library::getInstance();
    Book book("WAR");
    User user("Zunaira");
    Admin admin;
    switch (choice) {
        case 1:{
            library->displayBooks();
            break;
        }
        case 2:{
            book.borrowBook();
            break;
        }
        case 3:{
            book.returnBook();
            break;
        }
        case 4:{
            admin.addBookToLibrary(book);
            break;
        }
        case 5:{
            admin.removeBookFromLibrary("WAR");
            break;
        }
    }
    return 0;
}
