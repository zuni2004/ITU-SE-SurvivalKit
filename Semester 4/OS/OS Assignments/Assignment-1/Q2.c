#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char *argv[])
{
    int pid = getpid(); // the pid of the current running program
    printf("PID is: %d\n", pid);
    int rc = fork(); // created copy of the process

    if (rc < 0)
    {
        printf("Fork Failed\n");
        exit(1);
    }

    if (rc == 0)
    { // Child process
        int wc = wait(NULL); // for child to finish its execution than parent runs
        printf("I am child, pid: %d\n", getpid());
        sleep(2); // for simulating work in child
        printf("Child finished execution\n");
    }
    else
    {                        // Parent process
        printf("Parent here, My pid is %d\n", getpid());
    }
    return 0;
}
