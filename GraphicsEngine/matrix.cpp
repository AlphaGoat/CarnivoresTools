// Defines matrix object for rendering calculations
#include "matrix.h"


Matrix::Matrix(int r, int c) {
   num_rows = r;
   num_cols = c;
}

void Matrix::setElement(int i, int j, float val) {
    elements[i][j] = val;
}

float Matrix::getElement(int i, int j) {
    return elements[i][j];
}

Vector Matrix::getRow(int i) {
    Vector ret(num_cols);
    return ret;
}

Matrix Matrix::transpose() {
    Matrix transposeMat = Matrix(num_cols, num_rows);
    for (int i = 0; i < num_rows; i++) {
        for (int j = 0; j < num_cols; j++) {
            transposeMat.setElement(i, j, elements[j][i])
        }
    }

    return transposeMat;
}
