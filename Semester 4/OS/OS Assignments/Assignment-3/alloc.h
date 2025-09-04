#ifndef ALLOC_H
#define ALLOC_H

#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdbool.h>

#define PAGE_SIZE 4096 // fixed to 4KB //request for one memory page to OS
#define MINALLOC 8     // all memory blocks to be mul of 8

// linked list nodes struct
// MemoryBlock
typedef struct MemoryBlock
{
    size_t size;              // Represents the size of the memory block
    bool is_free;             // checks if block is free space or not
    struct MemoryBlock *next; // Points to the next node in LL
    void *addr;               // points to the start of the block
} MemoryBlock;

int init_alloc();        // calls the mmap() to allocaate the page also like sets up the linked list too
void *alloc(int size);   // allocates the memory fr the size requested
void dealloc(void *ptr); // for freeing the blocks at the given pointer
int cleanup();           // cleans up like free up all the memory

#endif
