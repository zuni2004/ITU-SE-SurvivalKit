//
// CREATED BY ZUNAIRA 10/05/2025
//

#include "alloc.h"

static void *memory = NULL;      // start of the memory
static MemoryBlock *head = NULL; // head of the linked list for the free space

int init_alloc()
{
    if (memory != NULL) // if memory has already been allocated
    {
        printf("List has already been allocated\n");
        return -1;
    }

    // if not than requesting the OS for 4kb of memoery by using mmap()
    memory = mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);

    if (memory == MAP_FAILED)
    {
        printf("mmap failed\n");
        return -1;
    }

    // create the first memory block
    head = (MemoryBlock *)malloc(sizeof(MemoryBlock));

    if (head == NULL)
    {
        printf("Malloc has failed\n");
        return -1;
    }

    // the first block
    head->size = PAGE_SIZE; // 4kb
    head->is_free = true;   // block is free so bool true
    head->next = NULL;      // no next block
    head->addr = memory;    // points to the start of the mmap memory

    return 0;
}

void *alloc(int size)
{
    // if size is a mul of 8 and if valid
    if (size <= 0 || size % MINALLOC != 0)
    {
        printf("Size is invalid\n");
        return NULL;
    }

    MemoryBlock *current = head; // pointer for traversal of linked list

    while (current != NULL) // to go to end of list to find the perfect size block
    {
        if (current->is_free && current->size >= size) // free block check and large enough size
        {
            // 2nd check to find the exact size
            if (current->size == size)
            {
                current->is_free = false; // mark it unfree
                return current->addr;     // return the start of the block
            }

            // if not found we make a block  of that size by splitting
            MemoryBlock *new_block = (MemoryBlock *)malloc(sizeof(MemoryBlock));

            if (new_block == NULL)
            {
                return NULL;
            }
            // set up the block of the desired size
            new_block->size = size;
            new_block->is_free = false;
            new_block->addr = current->addr;
            new_block->next = current;

            current->size -= size;                        // u[date the block size that is remaing]
            current->addr = (char *)current->addr + size; // start address forward is moved

            if (head == current)
            { // if the block is the head than header pointer to point on it
                head = new_block;
            }
            else // place the block linking it to the previous block
            {
                MemoryBlock *prev = head;
                while (prev != NULL && prev->next != current)
                {
                    prev = prev->next;
                }
                if (prev != NULL)
                {
                    prev->next = new_block;
                }
            }
            return new_block->addr;
        }
        current = current->next;
    }

    return NULL; // if you didny find the block for that size or nearly close enough
}

void dealloc(void *ptr)
{
    if (ptr == NULL || head == NULL) // if list is empty
    {
        printf("List is empty\n");
        return;
    }
    MemoryBlock *current = head; // pointer for traversal
    while (current != NULL)      // traversal to finf the block with the matching address
    {
        if (current->addr == ptr) // checking if adresses same
        {
            current->is_free = true; // mark as free

            if (current->next != NULL && current->next->is_free != false) // if next block exists and is also free than merge
            {
                current->size += current->next->size; // merge the size
                MemoryBlock *temp = current->next;    // save pointer to the next block so that you dont losr its address to link it to the nnext block
                current->next = current->next->next;  // connect it to the next and next block skipping the next block
                free(temp);                           // free
            }

            // if previous block is free than merge it it to the current block
            MemoryBlock *prev = NULL;
            MemoryBlock *iter = head;
            while (iter && iter != current)
            {
                prev = iter;
                iter = iter->next;
            }

            if (prev != NULL && prev->is_free != false)
            {
                prev->size += current->size;
                prev->next = current->next;
                free(current);
            }

            return;
        }
        current = current->next; // move to the next block
    }
}

int cleanup()
{
    if (memory == NULL)
    {
        return -1;
    }
    MemoryBlock *current = head;
    while (current != NULL)
    {
        MemoryBlock *next = current->next;
        free(current);
        current = next;
    }

    if (munmap(memory, PAGE_SIZE) != 0)
    {
        printf("munmap failed");
        return -1;
    }
    memory = NULL;
    head = NULL;
    return 0;
}
