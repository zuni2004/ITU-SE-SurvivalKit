#define CATCH_CONFIG_MAIN
#include "catch.hpp"
#include "Book.h"
#include "Library.h"
#include "User.h"
#include "Admin.h"


TEST_CASE("Admin functionalities", "[admin]") {
    Library* library = Library::getInstance();

    SECTION("Admin can add a book to the library") {
        Book b("War and Peace");
        Admin::addBookToLibrary(b);
        REQUIRE(library->findBook("War and Peace") != nullptr);

    }

    SECTION("Admin can remove a book from the library") {
        Book b("The Catcher in the Rye");
        library->addBooks(b);
        Admin::removeBookFromLibrary("The Catcher in the Rye");
        REQUIRE(library->findBook("The Catcher in the Rye") == nullptr);
    }
}
