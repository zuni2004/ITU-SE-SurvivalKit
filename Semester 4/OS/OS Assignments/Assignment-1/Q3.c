#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    int rc;             // to get the fork() system call values for the created new childs
    int pid = getpid(); // the pid of the current running program
    printf("PID is: %d\n", pid);
    for (int i = 1; i <= 3; i++) // for creating three kids
    {
        rc = fork(); // created copy of the parent
        if (rc < 0)
        {
            printf("Fork Failed\n");
            exit(1);
        }
        if (rc == 0)
        {             // Child process
            sleep(i); // for simulating work in child //sleeps 1s more than the previous
            printf("I am child %d, My pid: %d\n", i, getpid());
            exit(0); // exits successfully indicating work is done with no error
        }
    }
    for (int i = i; i <= 3; i++)
    {
        printf("This is parent, waiting for child %d\n", i);
        waitpid(-1, NULL, 0); // waitimg for any child to finish
    }
    printf("All three children finished working. Parent exiting.\n");
    return 0;
}
