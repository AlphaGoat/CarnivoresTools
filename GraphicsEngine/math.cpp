#include "matrix.h"


float vectormul(Vector *vec_a, Vector *vec_b) {
    float outval = 0.0;
    for (int i; i < vec_a->num_elements; i++) {
        for (int j; j < vec_b->num_elements; j++) {
            outval += vec_a->get_element(i) * vec_b->get_element(j);
        }
    }
    return outval;
}


void matmul(
    Matrix *matA, 
    Matrix *matB, 
    Matrix *outMat
) {

    // Check inner dimensions for compatibility
    if (matA->num_cols != matB->num_rows) {
        //error handling here
    }

    for (int i = 0; i < matA->num_rows; i++) {
        for (int j = 0; j < matB->num_cols; j++) {
            Vector vec_i = matA->getRow(i);
            Vector vec_j = matB->getCol(j);
            float c_ij = vectormul(&vec_i, &vec_j);
            outMat->setElement(i, j, c_ij);
        }
    }
}


