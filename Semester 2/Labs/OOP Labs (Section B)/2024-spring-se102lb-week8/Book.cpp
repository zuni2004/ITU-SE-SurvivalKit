#include "Book.h"

Book::Book() : title("") , available(true){

}

Book::Book(const string &t) : title(t) , available(true){

}

const string &Book::getTitle() const {
    return title;
}

bool Book::isAvailable() const {
    return true;
}

void Book::borrowBook() {
    available=false;
}

void Book::returnBook() {
    available= true;
}

ostream& operator<<(ostream& os, const Book& book){
    os<<"Title: "<<book.title<<"\nAvailable or not: "<<(book.available ? "Yes" : "No")<<endl;
    return os;
}

istream& operator>>(istream& is, Book& book){
    cout << "Enter title: ";
    is >>book.title ;
    return is;
}

