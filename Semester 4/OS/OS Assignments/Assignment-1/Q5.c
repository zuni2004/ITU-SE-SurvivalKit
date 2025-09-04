#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/time.h>

int main()
{
    struct timeval start;     // To store start time
    struct timeval end;       // To store end time
    long total_fork_time = 0; // To store total time for fork() calls

    // Measure timer overhead (cost of calling gettimeofday() multiple times)
    long avg_timer_overhead = 0;
    for (int i = 0; i < 1000000; i++) // Repeat 1,000,000 times for accuracy
    {
        gettimeofday(&start, NULL); // Start time
        gettimeofday(&end, NULL);   // endd time
        // Calculate time taken by gettimeofday() itself
        avg_timer_overhead = avg_timer_overhead + ((end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec));
    }
    avg_timer_overhead = avg_timer_overhead / 1000000; // Get average overhead

    // Measure fork() cost
    gettimeofday(&start, NULL);   // Start time before creating child processes
    for (int i = 0; i < 100; i++) // Loop to create 100 child processes
    {
        int rc = fork();
        if (rc < 0)
        {
            _exit(1); // Exit the program with an error code
        }
        if (rc == 0) // Child process
        {
            _exit(0); // Child exits immediately
        }
        else if (rc > 0) // parent process
        {
            wait(NULL); // waiting for child to finish
        }
    }
    gettimeofday(&end, NULL); // time end

    // Calculate total time taken for all fork() calls
    total_fork_time = (end.tv_sec - start.tv_sec) * 1000000 + (end.tv_usec - start.tv_usec);
    // Subtract timer overhead for more accurate fork() measurement
    total_fork_time -= avg_timer_overhead * 100;

    // Estimate cost per fork()
    double cost_per_fork = (double)total_fork_time / 100;
    // Calculate and display total cost and cost per fork()
    printf("Total cost for 100 fork() calls: %ld microseconds\n", total_fork_time);
    printf("Estimated cost per fork(): %.2f microseconds\n", cost_per_fork);
    return 0;
}
