#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/time.h>
#include <sched.h>

int main()
{
    int pipe0[2]; // Pipe for communication from parent to child
    int pipe1[2]; // Pipe for communication from child to parent
    struct timeval start;
    struct timeval end; // Variables to store start and end times
    int rc;

    // Create pipes
    if (pipe(pipe0) == -1 || pipe(pipe1) == -1)
    {
        printf("pipe failed");
        exit(1);
    }

    // Set CPU affinity to ensure both processes run on the same CPU
    // cpu_set_t mask;
    // int cpu = 0; // Set affinity to CPU 0
    // CPU_ZERO(&mask);
    // CPU_SET(cpu, &mask);
    // sched_setaffinity(0, sizeof(mask), &mask); // Bind to CPU 0

    // Create child process
    rc = fork();
    if (rc < 0)
    {
        printf("fork failed");
        exit(1); // exit woth error
    }

    if (rc == 0)
    { // Child process
        // Close unused pipe ends
        close(pipe0[1]); // Close write end of pipe0
        close(pipe1[0]); // Close read end of pipe1

        char buf;
        gettimeofday(&start, NULL); // Start time for child process

        for (int i = 0; i < 1000000; i++)
        {
            // Write to pipe0
            write(pipe0[1], "x", 1);
            // Read from pipe1
            read(pipe1[0], &buf, 1);
        }

        gettimeofday(&end, NULL); // End time for child process
        close(pipe0[0]);          // Close read end of pipe0
        close(pipe1[1]);          // Close write end of pipe1

        // Calculate total time taken for context switches
        long total_time = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec);
        printf("Child total time for %d iterations: %ld microseconds\n", 1000000, total_time);
        exit(0); // Exit child process
    }
    else
    { // Parent process
        // Close unused pipe ends
        close(pipe0[0]); // Close read end of pipe0
        close(pipe1[1]); // Close write end of pipe1

        char buf;
        gettimeofday(&start, NULL); // Start time for parent process

        for (int i = 0; i < 1000000; i++)
        {
            // Read from pipe0
            read(pipe0[0], &buf, 1);
            // Write to pipe1
            write(pipe1[1], "x", 1);
        }

        gettimeofday(&end, NULL); // End time for parent process
        close(pipe0[1]);          // Close write end of pipe0
        close(pipe1[0]);          // Close read end of pipe1

        // Wait for the child process to finish
        wait(NULL);

        // Calculate total time taken for context switches
        long total_time = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec);
        printf("Parent total time for %d iterations: %ld microseconds\n", 1000000, total_time);
    }

    return 0; // Exit successfully
}
