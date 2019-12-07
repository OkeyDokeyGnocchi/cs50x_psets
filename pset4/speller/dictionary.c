// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <strings.h>
#include <string.h>
#include <stdlib.h>

#include "dictionary.h"

// Represents number of buckets in a hash table
#define N 26

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Represents a hash table
node *hashtable[N];

// make a global variable for word count for size()
int word_count = 0;

// Hashes word to a number between 0 and 25, inclusive, based on its first letter
unsigned int hash(const char *word)
{
    return tolower(word[0]) - 'a';
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Initialize hash table
    for (int i = 0; i < N; i++)
    {
        hashtable[i] = NULL;
    }

    // Open dictionary
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        unload();
        return false;
    }

    // Buffer for a word
    char word[LENGTH + 1];

    // Insert words into hash table
    while (fscanf(file, "%s", word) != EOF)
    {
        // allocate memory for new node 'word'
        node *new_node = malloc(sizeof(node));
        // check that pointer isn't NULL, stop if it is
        if (!new_node)
        {
            unload();
            return false;
        }

        // add word to the node, set new_node->next to NULL for now, hash the word
        strcpy(new_node->word, word);
        new_node->next = NULL;
        int new_hash = hash(new_node->word);

        // increment word count
        word_count++;

        // check if the hash table has a non-NULL value
        // if NULL, set to new_node
        if (!hashtable[new_hash])
        {
            hashtable[new_hash] = new_node;
        }
        // if not NULL, add it to the end of the hash table index [new_hash]
        else
        {
            // make a pointer for swapping, ensure it isn't NULL
            for (node *swap_ptr = hashtable[new_hash]; swap_ptr != NULL; swap_ptr = swap_ptr->next)
            {
                // if swap_ptr isn't set for next
                if (!swap_ptr->next)
                {
                    swap_ptr->next = new_node;
                    break;
                }
            }
        }
    }

    // Close dictionary
    fclose(file);

    // Indicate success
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    // create a variable to pass back and set to global word_count
    int count = word_count;

    // if dictionary didn't load, word_count will still = 0
    if (count > 0)
    {
        return count;
    }

    // if word_count didn't increment, return 0
    return 0;
}

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // calculate the hash of the word we're checking
    int check_hash = hash(word);

    // create cursor in hash table index [check_hash]
    node *cursor = hashtable[check_hash];
    while (cursor != NULL)
    {
        // if strcasecmp returns 0, the strings are equal, return true
        if (strcasecmp(word, cursor->word) == 0)
        {
            return true;
        }
        // if cursor isn't NULL change cursor->next to iterate and keep checking
        cursor = cursor->next;

    }

    // if cursor hits NULL, the word isn't in the dictionary, return false
    return false;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // iterate thru all the indices of the hashtable
    for (int i = 0; i < N; i++)
    {
        node *cursor = hashtable[i];

        while (cursor != NULL)
        {
            node *tmp = cursor;
            cursor = cursor->next;
            free(tmp);
        }
    }
    return true;
}
