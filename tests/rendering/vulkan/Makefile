CFLAGS = -std=c++17 -O2
LDFLAGS = -lglfw -lvulkan -ldl -lpthread -lX11 -lXxf86vm -lXrandr -LXi

DinoTest: main.cpp
	g++ $(CFLAGS) -o DinoTest main.cpp $(LDFLAGS)

.PHONY: clean

clean:
	rm -f DinoTest