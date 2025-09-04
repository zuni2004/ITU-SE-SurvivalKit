#ifndef ODD_EVEN_THREADS_H
#define ODD_EVEN_THREADS_H

#include <stdio.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>
#include <semaphore.h>

typedef struct SharedData
{
    int n;                // N numbers to print til
    int current;          // cureent no being printed
    pthread_mutex_t lock; // mutex lock for thread sync
    pthread_cond_t cond;  // condition varibales used wiyh mutex
    sem_t odd_sem;        // semaphore to control odd T
    sem_t even_sem;       // for ecen T
} SharedData;

// Mutex
void *print_odd_mutex(void *arg);
void *print_even_mutex(void *arg);

// Condition variables
void *print_odd_cv(void *arg);
void *print_even_cv(void *arg);

// semaphore
void *print_odd_semaphore(void *arg);
void *print_even_semaphore(void *arg);

#endif
