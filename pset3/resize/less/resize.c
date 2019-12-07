#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#include "bmp.h"


int main(int argc, char *argv[])
{
    int n = atoi(argv[1]);
    if (argc != 4 || n <= 0 || strstr(argv[2], ".bmp") == NULL || strstr(argv[3], ".bmp") == NULL)
    {
        printf("Usage: ./resize n infile outfile\n");
        return 1;
    }
    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    // determine padding for scanlines
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;


    // keep the old values
    long inbi_biWidth = bi.biWidth;
    long inbi_biHeight = bi.biHeight;

    // edit the BITMAPINFOHEADER to account for n
    bi.biWidth *= n;
    bi.biHeight *= n;

    int outPadding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // edit the BITMAPFILEHEADER to account for n
    bi.biSizeImage = ((sizeof(RGBTRIPLE) * bi.biWidth) + outPadding) * abs(bi.biHeight);
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    // iterate over infile's scanlines #eachrow
    for (int i = 0, biHeight = abs(bi.biHeight) / n; i < biHeight; i++)
    {
        // repeat n times
        for (int lines = 0; lines < n; lines++)
        {
            // iterate over pixels in scanline #eachpixel
            for (int j = 0; j < (inbi_biWidth); j++)
            {
                // temporary storage
                RGBTRIPLE triple;

                // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

                // write RGB triple n - 1 times in a row
                for (int pix = 0; pix < n; pix++)
                {
                    // write RGB triple to outfile
                    fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                }
            }
            // add the padding
            for (int k = 0; k < outPadding; k++)
            {
                fputc(0x00, outptr);
            }
            if (lines < n - 1)
            {
                // use fseek to move the cursor back the length of the width times 3 for the triple
                // if you don't use the input original biWidth, you get random nonsense colors in output
                // because if it moves based on the new width * n it is super broken and great
                fseek(inptr, -(inbi_biWidth * sizeof(RGBTRIPLE)), SEEK_CUR);
            }

        }
        // skip over padding, if any
        fseek(inptr, padding, SEEK_CUR);
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}