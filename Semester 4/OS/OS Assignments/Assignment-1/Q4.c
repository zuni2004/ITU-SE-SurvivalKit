#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main()
{
    int pipefd[2]; //create a pipe with two file descriptors // one for reading and one for writing
    if (pipe(pipefd) == -1)
    {
        perror("pipe failed");
        exit(1);
    }
    pid_t child1 = fork(); //creates the first child process
    if (child1 == -1)
    {
        perror("fork failed");
        exit(1);
    }
    if (child1 == 0)
    {
        close(pipefd[0]);
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[1]);
        execlp("echo", "echo", "Hello, world!", NULL);
        perror("execlp failed");
        exit(1);
    }
    pid_t child2 = fork();
    if (child2 == -1)
    {
        perror("fork failed");
        exit(1);
    }

    if (child2 == 0)
    {
        close(pipefd[1]);
        dup2(pipefd[0], STDIN_FILENO);
        close(pipefd[0]);
        execlp("wc", "wc", "-c", NULL);
        perror("execlp failed");
        exit(1);
    }
    close(pipefd[0]);
    close(pipefd[1]);
    wait(NULL);
    wait(NULL);
    return 0;
}