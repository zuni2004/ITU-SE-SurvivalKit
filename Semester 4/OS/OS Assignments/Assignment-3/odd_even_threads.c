#include "odd_even_threads.h"

void *print_odd_mutex(void *arg)
{
    SharedData *data = (SharedData *)arg;

    // Keep running until we break manually
    while (1)
    {
        pthread_mutex_lock(&data->lock); // locking shared variable
        // If current number is greater than n, stop the loop
        if (data->current > data->n)
        {
            pthread_mutex_unlock(&data->lock); // unlock before breaking
            break;                             // Exit when current exceeds n
        }

        if (data->current % 2 != 0)
        {
            printf("%d\n", data->current);
            data->current++;
            pthread_cond_signal(&data->cond); // Notify even thread
        }

        pthread_mutex_unlock(&data->lock);
    }
    return NULL;
}

void *print_even_mutex(void *arg)
{
    SharedData *data = (SharedData *)arg;

    // Keep running until we break manually
    while (1)
    {
        pthread_mutex_lock(&data->lock); // locking shared variable
        // If current number is greater than n, stop the loop
        if (data->current > data->n)
        {
            pthread_mutex_unlock(&data->lock); // unlock before breaking
            break;
        }

        if (data->current % 2 == 0)
        {
            printf("%d\n", data->current);
            data->current++;
            pthread_cond_signal(&data->cond); // Notify odd thread
        }

        pthread_mutex_unlock(&data->lock);
    }
    return NULL;
}

void *print_odd_cv(void *arg)
{
    SharedData *data = (SharedData *)arg;
    pthread_mutex_lock(&data->lock); // locking once, will stay locked until done
    while (data->current <= data->n)
    {
        while (data->current % 2 == 0) // If current number is even, wait until even thread signals
        {
            pthread_cond_wait(&data->cond, &data->lock);
        }
        if (data->current <= data->n)
        {
            printf("%d\n", data->current);
            data->current++;
            pthread_cond_signal(&data->cond);
        }
    }
    pthread_mutex_unlock(&data->lock);
    return NULL;
}

void *print_even_cv(void *arg)
{
    SharedData *data = (SharedData *)arg;
    pthread_mutex_lock(&data->lock); // locking once, will stay locked until done
    while (data->current <= data->n)
    {
        while (data->current % 2 != 0) // If current number is odd, wait until even thread signals
        {
            pthread_cond_wait(&data->cond, &data->lock);
        }
        if (data->current <= data->n)
        {
            printf("%d\n", data->current);
            data->current++;
            pthread_cond_signal(&data->cond);
        }
    }
    pthread_mutex_unlock(&data->lock);
    return NULL;
}

void *print_odd_semaphore(void *arg)
{
    SharedData *data = (SharedData *)arg;
    while (1)
    {
        sem_wait(&data->odd_sem); // wait until its odd's turn
        if (data->current > data->n)
        {
            sem_post(&data->even_sem);
            break;
        }
        printf("%d\n", data->current);
        data->current++;
        sem_post(&data->even_sem);
    }
    return NULL;
}

void *print_even_semaphore(void *arg)
{
    SharedData *data = (SharedData *)arg;
    while (1)
    {
        sem_wait(&data->even_sem); // wait until its eevens turn
        if (data->current > data->n)
        {
            sem_post(&data->odd_sem);
            break;
        }
        printf("%d\n", data->current);
        data->current++;
        sem_post(&data->odd_sem);
    }
    return NULL;
}
