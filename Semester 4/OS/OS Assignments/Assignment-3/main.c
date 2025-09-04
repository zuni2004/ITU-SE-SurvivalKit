#include "alloc.h"
#include "odd_even_threads.h"

int main()
{
    int choice;

    printf("Assignment 4\n\n");
    printf("ZUNAIRA ABDUL AZIZ\nBSSE23058\n\n");
    printf("EASHAL YASIN\nBSSE23026\n\n");

    while (1)
    {
        printf("Choose an option:\n");
        printf("1: Custom Memory Manager\n");
        printf("2: Multi-Threaded Odd-Even Number Printing\n");
        printf("3: Exit\n");
        printf("Enter choice: ");
        scanf("%d", &choice);

        if (choice == 1)
        {
            printf("\n=== Memory Manager Demo ===\n");

            if (init_alloc() != 0)
            {
                printf("Error: Could not initialize memory manager.\n");
                continue;
            }

            char *a = alloc(64);
            char *b = alloc(128);
            char *c = alloc(200);
            char *d = alloc(512);

            printf("\nAllocated blocks:\n");
            printf("a (64B):  %p\n", a);
            printf("b (128B): %p\n", b);
            printf("c (200B): %p\n", c);
            printf("d (512B): %p\n", d);

            printf("\nFreeing blocks b and d...\n");
            dealloc(b);
            dealloc(d);

            char *e = alloc(120);
            printf("\nAllocated e (120B): %p\n", e);

            char *f = alloc(400);
            printf("Allocated f (400B): %p\n", f);

            char *g = alloc(3000);
            if (g == NULL)
            {
                printf("\nCould not allocate g (3000B): Not enough space\n");
            }
            else
            {
                printf("Allocated g (3000B): %p\n", g);
            }

            printf("\nCleaning up...\n");
            if (cleanup() != 0)
            {
                printf("Error: Cleanup failed.\n");
            }
        }
        else if (choice == 2)
        {
            int n;
            printf("\nEnter the value of N: ");
            scanf("%d", &n);

            SharedData data;
            data.n = n;
            data.current = 1;

            pthread_mutex_init(&data.lock, NULL);
            pthread_cond_init(&data.cond, NULL);
            sem_init(&data.odd_sem, 0, 1);
            sem_init(&data.even_sem, 0, 0);

            pthread_t thread_odd, thread_even;

            printf("\nWith Mutex\n");
            pthread_create(&thread_odd, NULL, print_odd_mutex, &data);
            pthread_create(&thread_even, NULL, print_even_mutex, &data);
            pthread_join(thread_odd, NULL);
            pthread_join(thread_even, NULL);
            data.current = 1;

            printf("\nWith Condition Variable\n");
            pthread_create(&thread_odd, NULL, print_odd_cv, &data);
            pthread_create(&thread_even, NULL, print_even_cv, &data);
            pthread_join(thread_odd, NULL);
            pthread_join(thread_even, NULL);
            data.current = 1;

            printf("\nWith Semaphore\n");
            pthread_create(&thread_odd, NULL, print_odd_semaphore, &data);
            pthread_create(&thread_even, NULL, print_even_semaphore, &data);
            pthread_join(thread_odd, NULL);
            pthread_join(thread_even, NULL);

            pthread_mutex_destroy(&data.lock);
            pthread_cond_destroy(&data.cond);
            sem_destroy(&data.odd_sem);
            sem_destroy(&data.even_sem);

            printf("\n");
        }
        else if (choice == 3)
        {
            printf("Exiting program.\n");
            break;
        }
        else
        {
            printf("Invalid choice. Please try again.\n");
        }
    }

    return 0;
}
