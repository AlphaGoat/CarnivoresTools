#include "image-utils.h"


uint8_t **convert_555_to_888_RGB(**uint16_t image_array, int width, int height) {
    /* Initialize a uint 8 bit RGB array */
    RGB **img_888bit[height]; 
    for (int i = 0; i < height; i++) {
        img_888bit[i] = (RGB*) malloc(width * sizeof(RGB));
    }

    uint8_t mask5 = 011111b;

    /* Convert 16-bit 555 data to 8-bit RGB */
    for (int i = 0; i < height; i++) {
        for (int j=0; j < width; j++) {
            pix555 = image_array[i][j];
            uint8_t b = (pix555 & mask5) << 3;
            uint8_t g = ((pix555 >> 5) & mask5) << 3;
            uint8_t r = ((pix555 >> (5 + 5)) & mask5) << 3;
            img_888bit[i][j]->r = r;
            img_888bit[i][j]->b = b;
            img_888bit[i][j]->g = g;

        }
    }

    return img_888bit;
}



