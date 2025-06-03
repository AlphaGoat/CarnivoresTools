objects = fluid_dynamics.o test_perlin.o

test_perlin: $(objects)
	g++ $^ -g -o test_perlin -std=c++11 -DWITHOUT_NUMPY -I/usr/include/python3.12 -lpython3.12 -lm

fluid_dynamics.o: fluid_dynamics.cpp
	g++ -g -c fluid_dynamics.cpp -o fluid_dynamics.o -ldl -lm 

test_perlin.o: test_perlin.cpp
	g++ -g -c test_perlin.cpp -o test_perlin.o -std=c++11 -DWITHOUT_NUMPY -I/usr/include/python3.12 -lpython3.12 -ldl -lm 

clean:
	rm -f *.o test_perlin