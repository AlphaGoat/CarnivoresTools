
class Vector {
    public:

        // Attributes
        int num_elements;
        float *elements;

        // Overloaded Operators
        float& operator[](int index) {
            return elements[index];
        }

        // Initializers
        Vector(int n) : num_elements(n) {}
        Vector(int n, float *vals): num_elements(n), elements(vals) {}

        // Methods
        float getElement(int i);
};


class Matrix {
    public:
        // Attributes
        int num_rows;
        int num_cols;
        float **elements;

        // Overloaded Operators
        Vector operator[](int index) {
            Vector outVector = Vector(num_cols, elements[index]);
            return outVector;
        }

        // Methods
        Matrix transpose();
        void setElement(int i, int j, float val);
        float getElement(int i, int j);
        Vector getRow(int i);
        Vector getCol(int j);
};


