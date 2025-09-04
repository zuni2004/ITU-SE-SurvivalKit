#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>    //for open()
#include <sys/wait.h> //for the wait()

int main(int argc, char *argv[])
{
    // Open the file with O_CREAT to create it if it doesn't exist, O_APPEND  for writing at the end of the file
    int fd = open("q1.txt", O_RDWR | O_CREAT | O_APPEND);
    // checks if file is opened or not, if system call value is -1 then it hasnt opened.
    if (fd < 0)
    {
        printf("Opening file failed, either it doesn't exist or hasn't opened\n");
        return -1;
    }

    int rc = fork();    // creates a new process of the pid
    if (rc < 0)
    {
        printf("Fork Failed\n");
        close(fd); //close the files before exiting
        return -1;
    }
    if (rc == 0)   // Child process
    {
        printf("Child process running and writing in the file\n");
        write(fd, "I am the child process. I am the one writing in the file.\n", 59);
        close(fd); //close the files before exiting
    }
    else   // Parent process
    {
        printf("Parent process running and writing in the file\n");
        write(fd, "I am the parent process. I am the one writing in the file.\n", 60);
        close(fd); //close the files before exiting
    }
    return 0;
}
