#include "string.h"

void *memcpy(void *dest, const void *src, size_t count)
{
	char *tmp = (char *)dest;
	const char *s = (const  char *)src;
	while (count--)
		*tmp++ = *s++;
	return dest;
}
