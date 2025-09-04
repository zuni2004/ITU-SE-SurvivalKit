all: ./a.out

compRun:
	g++ -std=c++11 main.cpp student.cpp student_linked_list.cpp -o r.out

compTest:
	g++ -std=c++11 test.cpp student.cpp student_linked_list.cpp -o a.out

compEvaluation:
	g++ -std=c++11 evaluation.cpp functions.cpp -o a.out

test: clean compTest; ./a.out

eval: clean compEvaluation; ./a.out

run: clean compRun; ./r.out

clean:
	rm -f *.out
