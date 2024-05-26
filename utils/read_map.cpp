#include <iostream>
#include <fstream>
using namespace std;

int read_map(string filepath) {
    ifstream map_buffer(filepath, ios::in|ios::binary);
    char input[1024];

    if (map_buffer.is_open()) {
        map_buffer.seekg(0, ios::beg);
        map_buffer.getline(input, 1024);
    }

    return 1;
}
