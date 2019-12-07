#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // check if correct number of arguments, print error if not
    if (argc != 2 || strstr(argv[1], ".raw") == NULL)
    {
        fprintf(stderr, "Usage: ./recover filename.raw\n");
        return 1;
    }

    // keep the input file name for later
    char *input_file = argv[1];

    // try to open the input file in read mode
    FILE *infile = fopen(input_file, "r");
    if (infile == NULL)
    {
        fprintf(stderr, "Could not open %s\n", input_file);
        return 2;
    }

    // declare variables for upcoming loop
    unsigned char buffer[512];
    int filenumber = 0;
    char *filename = malloc(sizeof(char) * 7);
    FILE *outfile;

    // find start of JPEG
    while (fread(buffer, 1, 512, infile))
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // open new JPEG if headers found
            sprintf(filename, "%03i.jpg", filenumber);
            outfile = fopen(filename, "w");
            filenumber++;

        }

        // write 512 bytes to JPEG
        fwrite(buffer, 1, 512, outfile);


    }

    fclose(infile);
    free(filename);
    return 0;
}
